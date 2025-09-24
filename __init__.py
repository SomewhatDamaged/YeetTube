from .yeettube import YeetTube


async def setup(bot):
    await bot.add_cog(YeetTube(bot))
