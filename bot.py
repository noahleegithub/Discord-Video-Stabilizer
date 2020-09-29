# -*- coding: utf-8 -*-
"""
Created on Wed Sep  9 00:04:20 2020

@author: Noah Lee, lee.no@northeastern.edu
"""
import time
import hashlib
import os
import youtube_dl

from discord.ext import commands
from discord import File
from discord import Embed
from stab_vid import StabVid
from exceptions import StabbotException, VideoDownloadingException

class Stabbot(commands.Bot):
    
    def __init__(self, command_prefix, description, token):
        super().__init__(command_prefix=command_prefix, 
                         description=description)
        self.token = token
        
    def run(self):
        ''' Makes the bot begin listening to Discord.

        Returns
        -------
        None.
        '''
        super().run(self.token)
        
        
    @commands.Bot.event
    async def on_ready():
        ''' States when the bot is listening to Discord and lists the number
            and names of the guilds it is listening to.

        Returns
        -------
        None.
        '''
        username = super().user.name
        guilds = super().guilds
        print(f'{username} has connected to Discord!')
        print(f'Listening to {len(guilds)} guilds:')
        for guild in guilds:
            print(guild.name)
    
    @commands.Bot.command(name='vid',
                          description=("Performs video stabilization on "
                                       + "embedded or attached videos."))
    async def stab_vid(ctx):
        ''' Stabilizes any videos the user gives to the bot.

        Parameters
        ----------
        ctx : 
            Discord message context. Used for sending and receiving messages.

        Raises
        ------
        VideoDownloadingException
            If there was a problem downloading the video.

        Returns
        -------
        None.
        '''
        time.sleep(0.5)
    
        try:
            
            msg = ctx.message
            fnames = await Stabbot.download_attachments(msg) \
                + Stabbot.download_embeds(msg)
            if len(fnames) == 0:
                raise VideoDownloadingException("Did not detect any videos.")
                
            await ctx.send("Processing . . .")
                
            stabilizer = StabVid()
            for fname in fnames:
                fname = fname + ".mp4"
                out_fname = os.path.join("videos", "out_" + os.path.basename(fname))
                stabilizer(os.path.abspath(fname), os.path.abspath(out_fname))
                    
            await ctx.send("Your videos have been stabilized!")
            for dirpath, dirnames, filenames in os.walk("videos"):
                for file in filenames:
                    if file.startswith("out"):
                        await ctx.send(file=File(os.path.join(dirpath, file)))
                        
            for dirpath, dirnames, filenames in os.walk("videos"):
                for file in filenames:
                    os.remove(os.path.join(dirpath, file))                                
        except StabbotException as stexc:
            print("Stabbot Exception:")
            print(stexc.args)
            await ctx.send(stexc.args[0])
            return
                                
    async def download_attachments(msg):
        ''' Downloads videos that are attached to a message.

        Parameters
        ----------
        msg : discord.Message
            A dictionary that represents a Discord message. The attribute
            we are interested in is .attachments.

        Raises
        ------
        VideoDownloadingException
            If there was an error while downloading the attachment.

        Returns
        -------
        fnames : List of strings
            A list of filenames in the /videos folder where the attachments
            were saved.
        '''
        try:
            fnames = []
            for attachment in msg.attachments:
                fname = os.path.join("videos", str(attachment.id))
                await attachment.save(fname)
                fnames.append(fname)
                return fnames
        except Exception as exc:
            print("Error downloading attachments:", type(exc), exc.args)
            raise VideoDownloadingException("Unable to save videos from"
                                            + " attached files.")
    
    def download_embeds(msg):
        ''' Uses urls contained within a Discord message's embeds to download
            videos.

        Parameters
        ----------
        msg : discord.Message
            A dictionary containing information about a Discord message. In 
            this case, we are only concerned with the .embeds attribute.

        Raises
        ------
        VideoDownloadingException
            If youtube_dl was unable to download the video from the url. 
            Usually due to a malformed url or an unsupported website.

        Returns
        -------
        fnames : List of strings
            Represents the filenames of downloaded videos in the /videos 
            directory.
        '''
        try:
            urls = Stabbot.extract_embedded_urls(msg)
            fnames = []
            for url in urls:
                fname = hashlib.md5(url.encode('utf-8')).hexdigest()
                full_fname = os.path.join("videos", fname)
                ydl = youtube_dl.YoutubeDL({
                    "outtmpl": full_fname,
                    "quiet": True,
                    "restrictfilenames": True})
                ydl.download([url])
                fnames.append(full_fname)
                return fnames
        except Exception as exc:    
            print("Error downloading embeds:", type(exc), exc.args)
            raise VideoDownloadingException("Unable to download videos from"
                                            + " embedded urls.")
    
    def extract_embedded_urls(msg):
        ''' Returns the urls of every video embedded in the message.

        Parameters
        ----------
        msg : discord.Message
            A dictionary containing information about a Discord message
            including embedded content.

        Returns
        -------
        embedded_urls : List of strings
            A list containing string urls to every video embedded in the msg.
        '''
        embedded_vids = [embed.video for embed in msg.embeds]
        embedded_urls = []
        for embedded_vid in embedded_vids:
            if embedded_vid != Embed.Empty:
                embedded_urls.append(embedded_vid.url)
        return embedded_urls
        