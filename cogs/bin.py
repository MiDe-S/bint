from nextcord.ext import commands
from dictionaries import *
from character_dictionary import CharacterDictionary
from amiibo_functions import BinManager
from amiibo import AmiiboMasterKey
from ssbu_amiibo import SsbuAmiiboDump as AmiiboDump
from nextcord import File
import io
import re
from nextcord import slash_command
from nextcord import Interaction, SlashOption

default_assets_location = r"Brain_Transplant_Assets"
characters_location = r"Brain_Transplant_Assets/characters.xml"
char_dict = CharacterDictionary(characters_location)
binmanagerinit = BinManager(char_dict)


class binCog(commands.Cog):
    @commands.command(name="bineval")
    async def bineval(self, ctx):
        await ctx.send(binmanagerinit.bineval(await ctx.message.attachments[0].read()))
    
    @commands.command(name="convert")
    @commands.dm_only()
    async def convert_nfc_tools_file_to_bin(self, ctx):
        vb = []
        for files in ctx.message.attachments:
          export_string_lines = None
          hex = ""
          file = await files.read()
          file = str(file, 'utf-8')
          print(file)
          export_string_lines = file.splitlines()

          for line in export_string_lines:
            match = re.search(r"(?:[A-Fa-f0-9]{2}:){3}[A-Fa-f0-9]{2}", line)
            if match:
              hex = hex + match.group(0).replace(":", "")

          bin = bytes.fromhex(hex)
          print(len(bin))
          if len(bin) == 540:
            vb.append(File(io.BytesIO(bin), str(files.filename).strip('.txt') + ".bin"))
            
          else:
            await ctx.send("Invalid text file.")
        if len(vb) == 0:
          return
        else:
          await ctx.send(
              files=vb
            )

    @commands.command(name="transplant")
    @commands.dm_only()
    async def brain_transplant(self, ctx, *, character):
        try:
            character = character
            v = binmanagerinit.transplant(
                  character=character.title(),
                  randomize_SN=True,
                  dump = await ctx.message.attachments[0].read()
                )
            vb = File(io.BytesIO(v), filename = ctx.message.attachments[0].filename)
            await ctx.send(file=vb)
        except KeyError:
            try:
                character = TRANSLATION_TABLE_CHARACTER_TRANSPLANT[
                    character.replace(" ", "")
                ]
                v = binmanagerinit.transplant(
                  character=character.title(),
                  randomize_SN=True,
                  dump = await ctx.message.attachments[0].read()
                )
                vb = File(io.BytesIO(v), filename = ctx.message.attachments[0].filename)
                await ctx.send(file=vb)
            except KeyError:
                await ctx.send(f"'{character}' is an invalid character.")

    @commands.command(name="shufflesn")
    @commands.dm_only()
    async def shufflenfpsn(self, ctx):
        vb = []
        for files in ctx.message.attachments:
          v = binmanagerinit.randomize_sn(dump_=await files.read())
          vb.append(File(io.BytesIO(v.data), filename = files.filename))
        await ctx.send(files=vb)

    @commands.command(name="setspirits")
    @commands.dm_only()
    async def spiritedit(
        self, ctx, attack, defense, ability1="none", ability2="none", ability3="none"
    ):
        print(ability1)
        print(ability2)
        print(ability3)
        try:
            v = binmanagerinit.setspirits(
                attack,
                defense,
                ability1,
                ability2,
                ability3,
                dump = await ctx.message.attachments[0].read()
            )
            vb = File(io.BytesIO(v), filename = ctx.message.attachments[0].filename)
            await ctx.send(
                f"{attack}, {defense}",
                file=vb,
            )
        except IndexError:
            await ctx.send("Illegal Setup")

    @commands.command(name="rename")
    @commands.dm_only()
    async def rename(self, ctx, *, newamiiboname):

        with open(r"/".join([default_assets_location, "key_retail.bin"]), "rb") as fp_j:
            master_keys = AmiiboMasterKey.from_combined_bin(fp_j.read())
        dump = AmiiboDump(master_keys, await ctx.message.attachments[0].read())
        dump.unlock()
        dump.amiibo_nickname = newamiiboname
        dump.lock()
        vb = File(io.BytesIO(dump.data), filename = ctx.message.attachments[0].filename)

        await ctx.send(file=vb)

    @commands.command(name="decrypt")
    @commands.is_owner()
    async def decrypt(self, ctx):
        v = binmanagerinit.decrypt(await ctx.message.attachments[0].read())
        vb = File(io.BytesIO(v), filename = ctx.message.attachments[0].filename)
        await ctx.send(file=vb)

    @commands.command(name="binedit")
    @commands.is_owner()
    async def binedit(self, ctx, offset, bit_index, number_of_bits, value):
        v = binmanagerinit.personalityedit(await ctx.message.attachments[0].read(), offset, bit_index, number_of_bits, value)
        vb = File(io.BytesIO(v), filename = ctx.message.attachments[0].filename)
        await ctx.send(file=vb)


def setup(bot):
    bot.add_cog(binCog(bot))
