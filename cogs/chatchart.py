__copying__ = """
By Twentysix26: https://github.com/aikaterna/aikaterna-cogs/blob/v3/chatchart/chatchart.py
Edited by HarJIT.

In original:

#  Lines 72 through 90 (edit: of original) are influenced heavily by cacobot's stats module:
#  https://github.com/Orangestar12/cacobot/blob/master/cacobot/stats.py
#  Big thanks to Redjumpman for changing the beta version from 
#  Imagemagick/cairosvg to matplotlib.
#  Thanks to violetnyte for suggesting this cog.

https://github.com/aikaterna/aikaterna-cogs/blob/master/LICENSE contains:

MIT License

Copyright (c) 2016 

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE."""

import discord
import heapq
import os
from io import BytesIO
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
plt.switch_backend('agg')
from discord.ext import commands


class Chatchart:
    """Show activity."""

    def __init__(self, bot):
        self.bot = bot

    def create_chart(self, top, others, channel):
        plt.clf()
        sizes = [x[1] for x in top]
        labels = ["{} {:g}%".format(x[0], x[1]) for x in top]
        if len(top) >= 20:
            sizes = sizes + [others]
            labels = labels + ["Others {:g}%".format(others)]
        if len(channel.name) >= 19:
            channel_name = '{}...'.format(channel.name[:19])
        else:
            channel_name = channel.name
        title = plt.title("Stats in #{}".format(channel_name), color="white")
        title.set_va("top")
        title.set_ha("center")
        plt.gca().axis("equal")
        colors = ['r', 'darkorange', 'gold', 'y', 'olivedrab', 'green', 'darkcyan', 'mediumblue', 'darkblue', 'blueviolet', 'indigo', 'orchid', 'mediumvioletred', 'crimson', 'chocolate', 'yellow', 'limegreen','forestgreen','dodgerblue','slateblue','gray']
        pie = plt.pie(sizes, colors=colors, startangle=0)
        plt.legend(pie[0], labels, bbox_to_anchor=(0.7, 0.5), loc="center", fontsize=10,
                   bbox_transform=plt.gcf().transFigure, facecolor='#ffffff')
        plt.subplots_adjust(left=0.0, bottom=0.1, right=0.45)
        image_object = BytesIO()
        plt.savefig(image_object, format='PNG', facecolor='#36393E')
        image_object.seek(0)
        return image_object

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.channel)
    async def chatchart(self, ctx, channel: discord.TextChannel=None, messages=5000, havebot=0):
        """
        Generates a pie chart, representing the last 5000 messages in the specified channel.
        """
        e = discord.Embed(description="Loading...", colour=0x00ccff)
        e.set_thumbnail(url="https://i.imgur.com/vSp4xRk.gif")
        em = await ctx.send(embed=e)
		
        if channel is None:
            channel = ctx.message.channel
        history = []
        if not channel.permissions_for(ctx.message.author).read_messages == True:
            await em.delete()
            return await ctx.send("You're not allowed to access that channel.")
        try:
            async for msg in channel.history(limit=messages):
                history.append(msg)
        except discord.errors.Forbidden:
            await em.delete()
            return await ctx.send("No permissions to read that channel.")
        msg_data = {'total count': 0, 'users': {}}

        for msg in history:
            if len(msg.author.name) >= 20:
                short_name = '{}...'.format(msg.author.name[:20])
            else:
                short_name = msg.author.name
            whole_name = '{}#{}'.format(short_name, msg.author.discriminator)
            if msg.author.bot and not havebot:
                pass
            elif whole_name in msg_data['users']:
                msg_data['users'][whole_name]['msgcount'] += 1
                msg_data['total count'] += 1
            else:
                msg_data['users'][whole_name] = {}
                msg_data['users'][whole_name]['msgcount'] = 1
                msg_data['total count'] += 1

        for usr in msg_data['users']:
            pd = float(msg_data['users'][usr]['msgcount']) / float(msg_data['total count'])
            msg_data['users'][usr]['percent'] = round(pd * 100, 1)

        top_ten = heapq.nlargest(20, [(x, msg_data['users'][x][y])
                                      for x in msg_data['users']
                                      for y in msg_data['users'][x]
                                      if y == 'percent'], key=lambda x: x[1])
        others = 100 - sum(x[1] for x in top_ten)
        img = self.create_chart(top_ten, others, channel)
        await em.delete()
        await ctx.message.channel.send(file=discord.File(img, 'chart.png'))

def setup(mybot):
    mybot.add_cog(Chatchart(mybot))



