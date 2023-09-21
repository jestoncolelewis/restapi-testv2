import pulumi
import pulumi_archive as archive
import pulumi_aws as aws
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
iam_for_lambda = aws.iam.Role(
    "iamForLambda",
    assume_role_policy=assume_role.json,
)
lambda_basic_attach = aws.iam.RolePolicyAttachment(
    'lambdaBasicPolicyAttach',
    role=iam_for_lambda.name,
    policy_arn='arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
)
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
    runtime="python3.9",
    environment={
        "variables": {
            "LOG_LEVEL": "INFO"
        }
    }
)

# Create api
apigw = aws.apigatewayv2.Api(
    "httpAPI", 
    protocol_type="HTTP"
)
route = aws.apigatewayv2.Route(
    "route",
    api_id=apigw.id,
    route_key="GET /prod"
)
integration = aws.apigatewayv2.Integration(
    "integration",
    api_id=apigw.id,
    content_handling_strategy="CONVERT_TO_TEXT",
    integration_type="HTTP_PROXY",
    integration_method="GET",
    integration_uri=get_function.arn
)
stage = aws.apigatewayv2.Stage(
    "stage",
    api_id=apigw.id,
)
deployment = aws.apigatewayv2.Deployment(
    "deployment",
    api_id=apigw.id
)

# Export the URLs and hostnames of the bucket and distribution.
pulumi.export("originURL", pulumi.Output.concat("http://", bucket.website_endpoint))
pulumi.export("originHostname", bucket.website_endpoint)
pulumi.export("cdnURL", pulumi.Output.concat("https://", cdn.domain_name))
pulumi.export("cdnHostname", cdn.domain_name)
pulumi.export("apiEndpoint", apigw.api_endpoint)
with open("./README.md") as f:
    pulumi.export("readme", f.read())
