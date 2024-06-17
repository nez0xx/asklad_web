import httpx


async def parse_file(filename):

    url = 'http://127.0.0.1:9000/upload'
    response = httpx.post(url, data={'filename': filename})
    print(response.read())
    print(response.json())
    return response.json()
