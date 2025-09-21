from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from urllib.parse import urlencode
import asyncio
import json
import requests

base_url = "https://server.smithery.ai/@falahgs/flux-imagegen-mcp-server/mcp"
params = {"api_key": "5cba1d1c-7ce8-48c9-bf0b-e77955eea543"}
url = f"{base_url}?{urlencode(params)}"

async def generate_image(prompt: str, width: int = 512, height: int = 512):
    async with streamablehttp_client(url) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # List tools
            tools_result = await session.list_tools()
            image_tool = next((t for t in tools_result.tools if "image" in t.name.lower()), None)
            if not image_tool:
                print("Image generation tool not found")
                return
            
            # Call the tool
            result = await session.call_tool(
                image_tool.name,
                {
                    "prompt": prompt,
                    "width": width,
                    "height": height,
                }
            )

            # Extract JSON from TextContent
            if hasattr(result, "content") and isinstance(result.content, list):
                text_obj = result.content[0]
                if hasattr(text_obj, "text"):
                    data = json.loads(text_obj.text)
                    image_url = data.get("imageUrl")
                    print("Generated image URL:", image_url)

                    # Optional: download and save image
                    response = requests.get(image_url)
                    if response.status_code == 200:
                        with open("generated_image.png", "wb") as f:
                            f.write(response.content)
                        print("Image saved as generated_image.png")
                    else:
                        print("Failed to download image")
            else:
                print("Unexpected result format:", result)

if __name__ == "__main__":
    prompt = "A futuristic cityscape at sunset, highly detailed, cinematic lighting"
    asyncio.run(generate_image(prompt))
