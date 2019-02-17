access_key = 'AKIAIEX6LYVOWOU63THA'
secret_key = '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'
associate_tag = 'erickmhq-21'
region = 'ES'

from amazon.api import AmazonAPI
amazon = AmazonAPI(
    aws_key = access_key,
    aws_secret = secret_key,
    aws_associate_tag = associate_tag,
    region = region
)

# products = amazon.search_n(1, Keywords='Reloj')
# print(products[0].title)

product = amazon.lookup(ItemId='B00EOE0WKQ')

