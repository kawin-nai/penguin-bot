import json
import os

import discord
from discord.ext import commands
import requests


class DictionaryCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="define", aliases=["def"])
    async def define(self, ctx, *args):
        endpoint = "entries"
        language_code = "en-us"
        # word = "record"
        word = " ".join(args)
        url = "https://od-api.oxforddictionaries.com/api/v2/" + endpoint + "/" + language_code + "/" + word.lower()
        response = requests.get(url, headers={"app_id": os.getenv("OXFORD_APP_ID"), "app_key": os.getenv("OXFORD_APP_KEY")})
        if response.status_code == 200:
            data = response.json()
            # pretty print data
            print(json.dumps(data, indent=4, sort_keys=True))

            # Get up to 3 definitions, part of speech, and example sentences
            definitions = []
            for i in range(3):
                try:
                    definitions.append(
                        data["results"][0]["lexicalEntries"][i]["entries"][0]["senses"][0]["definitions"][0])
                except:
                    break
            print(definitions)

            part_of_speech = []
            for i in range(3):
                try:
                    part_of_speech.append(data["results"][0]["lexicalEntries"][i]["lexicalCategory"]["text"])
                except:
                    break
            print(part_of_speech)

            examples = []
            for i in range(3):
                try:
                    examples.append(
                        data["results"][0]["lexicalEntries"][i]["entries"][0]["senses"][0]["examples"][0]["text"])
                except:
                    break
            print(examples)

            embed = discord.Embed(title=word.capitalize(), color=0x00ff00)
            for i in range(len(definitions)):
                embed.add_field(name=part_of_speech[i], value=definitions[i].capitalize(), inline=False)
                embed.add_field(name="Example", value=examples[i].capitalize(), inline=False)
            await ctx.send(embed=embed)

        else:
            embed = discord.Embed(title="Error", color=0xff0000)
            embed.add_field(name="Error", value="Please try again", inline=False)
            await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(DictionaryCog(bot))
