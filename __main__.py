import pulumi
import pulumi_archive as archive
import pulumi_aws as aws
import pulumi_aws_apigateway as apigateway
import pulumi_synced_folder as synced_folder

# Import the program's configuration settings.
path = "./www"
index_document = "index.html"
error_document = "error.html"

# Create an S3 bucket and configure it as a website.
bucket = aws.s3.Bucket(
    "bucket",
    website=aws.s3.BucketWebsiteArgs(
        index_document=index_document,
        error_document=error_document,
    ),
)

# Set ownership controls for the new bucket
ownership_controls = aws.s3.BucketOwnershipControls(
    "ownership-controls",
    bucket=bucket.id,
    rule=aws.s3.BucketOwnershipControlsRuleArgs(
        object_ownership="ObjectWriter",
    )
)

# Configure public ACL block on the new bucket
public_access_block = aws.s3.BucketPublicAccessBlock(
    "public-access-block",
    bucket=bucket.id,
    block_public_acls=False,
)

# Use a synced folder to manage the files of the website.
bucket_folder = synced_folder.S3BucketFolder(
    "bucket-folder",
    acl="public-read",
    bucket_name=bucket.bucket,
    path=path,
    opts=pulumi.ResourceOptions(depends_on=[
        ownership_controls,
        public_access_block
    ])
)

# Create a CloudFront CDN to distribute and cache the website.
cdn = aws.cloudfront.Distribution(
    "cdn",
    enabled=True,
    origins=[
        aws.cloudfront.DistributionOriginArgs(
            origin_id=bucket.arn,
            domain_name=bucket.website_endpoint,
            custom_origin_config=aws.cloudfront.DistributionOriginCustomOriginConfigArgs(
                origin_protocol_policy="http-only",
                http_port=80,
                https_port=443,
                origin_ssl_protocols=["TLSv1.2"],
            ),
        )
    ],
    default_cache_behavior=aws.cloudfront.DistributionDefaultCacheBehaviorArgs(
        target_origin_id=bucket.arn,
        viewer_protocol_policy="redirect-to-https",
        allowed_methods=[
            "GET",
            "HEAD",
            "OPTIONS",
        ],
        cached_methods=[
            "GET",
            "HEAD",
            "OPTIONS",
        ],
        default_ttl=600,
        max_ttl=600,
        min_ttl=600,
        forwarded_values=aws.cloudfront.DistributionDefaultCacheBehaviorForwardedValuesArgs(
            query_string=True,
            cookies=aws.cloudfront.DistributionDefaultCacheBehaviorForwardedValuesCookiesArgs(
                forward="all",
            ),
        ),
    ),
    price_class="PriceClass_100",
    custom_error_responses=[
        aws.cloudfront.DistributionCustomErrorResponseArgs(
            error_code=404,
            response_code=404,
            response_page_path=f"/{error_document}",
        )
    ],
    restrictions=aws.cloudfront.DistributionRestrictionsArgs(
        geo_restriction=aws.cloudfront.DistributionRestrictionsGeoRestrictionArgs(
            restriction_type="none",
        ),
    ),
    viewer_certificate=aws.cloudfront.DistributionViewerCertificateArgs(
        cloudfront_default_certificate=True,
    ),
)

# Create function
assume_role = aws.iam.get_policy_document(
    statements=[
        aws.iam.GetPolicyDocumentStatementArgs(
            effect="Allow",
            principals=[aws.iam.GetPolicyDocumentStatementPrincipalArgs(
                type="Service",
                identifiers=["lambda.amazonaws.com"]
            )],
            actions=["sts:AssumeRole"]
        )
    ]
)
iam_for_lambda = aws.iam.Role("iamForLambda", assume_role_policy=assume_role.json)
get_lambda = archive.get_file(
    type="zip",
    source_file="get_function.py",
    output_path="lambda_get_payload.zip"
)
get_function = aws.lambda_.Function(
    "get_func",
    code=pulumi.FileArchive("lambda_get_payload.zip"),
    role=iam_for_lambda.arn,
    handler="get_function.handler",
    runtime="python3.9"
)

# Create api
api = aws.apigateway.RestApi("api")
deployment = aws.apigateway.Deployment(
    "Deployment",
    rest_api=api.id
)
resource = aws.apigateway.Resource(
    "Resource",
    rest_api=api.id,
    parent_id=api.root_resource_id,
    path_part="prod"
)
get_method = aws.apigateway.Method(
    "GetMethod",
    rest_api=api.id,
    resource_id=resource.id,
    http_method="GET",
    authorization="NONE"
)
get_integration = aws.apigateway.Integration(
    "GetIntegration",
    rest_api=api.id,
    resource_id=resource.id,
    http_method=get_method.http_method,
    integration_http_method="POST",
    type="AWS_PROXY",
    uri=get_function.invoke_arn
)
options_method = aws.apigateway.Method(
    "OptionsMethod",
    rest_api=api.id,
    resource_id=resource.id,
    http_method="OPTIONS",
    authorization="NONE"
)
options_integration = aws.apigateway.Integration(
    "OptionsIntegration",
    rest_api=api.id,
    resource_id=resource.id,
    http_method=options_method.http_method,
    type="MOCK"
)
response200 = aws.apigateway.MethodResponse(
    "response200",
    rest_api=api.id,
    resource_id=resource.id,
    http_method=options_method.http_method,
    status_code="200"
)
integration_response = aws.apigateway.IntegrationResponse(
    "IntegrationResponse",
    rest_api=api.id,
    resource_id=resource.id,
    http_method=options_method.http_method,
    status_code=response200.status_code,
    response_templates={
        "application/xml": """
                                #set($inputRoot = $input.path('$'))
                                <?xml version="1.0" encoding="UTF-8"?>
                                <message>
                                    $inputRoot.body
                                </message>
                            """
    }
)
stage = aws.apigateway.Stage(
    "Stage",
    deployment=deployment.id,
    rest_api=api.id,
    stage_name="stage"
)

# Export the URLs and hostnames of the bucket and distribution.
pulumi.export("originURL", pulumi.Output.concat("http://", bucket.website_endpoint))
pulumi.export("originHostname", bucket.website_endpoint)
pulumi.export("cdnURL", pulumi.Output.concat("https://", cdn.domain_name))
pulumi.export("cdnHostname", cdn.domain_name)
pulumi.export("apiURL", stage.invoke_url)
