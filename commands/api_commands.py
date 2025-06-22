"""
API-related Discord commands extracted from bot.py to fix God Object anti-pattern.
Contains commands that interact with external APIs like memes, NASA, Valorant, etc.
"""

import discord
from discord import app_commands
from api_manager import APIManager


class ValorantSkin:
    """Domain object for Valorant skin data to fix Feature Envy."""
    
    def __init__(self, data: dict):
        self._data = data
        self.display_name = data.get('displayName', 'Unknown')
        self.display_icon = data.get('displayIcon', '')
        self.chromas = data.get('chromas', [])
        self.levels = data.get('levels', [])
    
    def matches_search(self, search_term: str) -> bool:
        """Check if this skin matches the search term."""
        return search_term.lower() in self.display_name.lower()
    
    def create_embed(self) -> discord.Embed:
        """Create a Discord embed for this skin."""
        embed = discord.Embed(title=self.display_name, color=0x00ff00)
        if self.display_icon:
            embed.set_image(url=self.display_icon)
        
        if self.chromas:
            chroma_names = [chroma.get('displayName', 'Unknown') for chroma in self.chromas[:3]]
            embed.add_field(name="Available Chromas", value=", ".join(chroma_names), inline=False)
        
        if self.levels:
            embed.add_field(name="Upgrade Levels", value=str(len(self.levels)), inline=True)
        
        return embed


class APICommands:
    """Handles API-related Discord bot commands."""
    
    def __init__(self, tree: app_commands.CommandTree, api_manager: APIManager):
        self.tree = tree
        self.api_manager = api_manager
        self._register_commands()
    
    def _register_commands(self):
        """Register all API-related commands."""
        
        @self.tree.command(name="meme", description="Sends a random meme")
        async def meme(interaction: discord.Interaction):
            await interaction.response.defer(thinking=True)
            
            meme_data = await self.api_manager.get_meme()
            if isinstance(meme_data, str):  # Error message
                await interaction.followup.send(meme_data)
                return
            
            embed = discord.Embed(title=meme_data.get('title', 'Random Meme'), color=0x00ff00)
            embed.set_image(url=meme_data['url'])
            embed.set_footer(text=f"👍 {meme_data.get('ups', 0)} | r/{meme_data.get('subreddit', 'unknown')}")
            
            await interaction.followup.send(embed=embed)

        @self.tree.command(name="insult", description="Sends a random insult")
        async def insult(interaction: discord.Interaction):
            await interaction.response.defer(thinking=True)
            
            insult_text = await self.api_manager.get_insult()
            embed = discord.Embed(title="Random Insult", description=insult_text, color=0xff0000)
            
            await interaction.followup.send(embed=embed)

        @self.tree.command(name="advice", description="Sends random advice")
        async def advice(interaction: discord.Interaction):
            await interaction.response.defer(thinking=True)
            
            advice_text = await self.api_manager.get_advice()
            embed = discord.Embed(title="Random Advice", description=advice_text, color=0x0099ff)
            
            await interaction.followup.send(embed=embed)

        @self.tree.command(name="fact", description="Sends a random useless fact")
        async def fact(interaction: discord.Interaction):
            await interaction.response.defer(thinking=True)
            
            fact_text = await self.api_manager.get_useless_fact()
            embed = discord.Embed(title="Useless Fact", description=fact_text, color=0x9932cc)
            
            await interaction.followup.send(embed=embed)

        @self.tree.command(name="adop", description="Sends NASA's Astronomy Picture of the Day")
        async def adop(interaction: discord.Interaction):
            await interaction.response.defer(thinking=True)
            
            adop_data = await self.api_manager.get_adop()
            if isinstance(adop_data, str):  # Error message
                await interaction.followup.send(adop_data)
                return
            
            embed = discord.Embed(title=adop_data.get('title', 'Astronomy Picture of the Day'), color=0x000080)
            embed.add_field(name="Date", value=adop_data.get('date', 'Unknown'), inline=True)
            
            if adop_data.get('explanation'):
                # Truncate explanation if too long for Discord embed
                explanation = adop_data['explanation']
                if len(explanation) > 1024:
                    explanation = explanation[:1021] + "..."
                embed.add_field(name="Explanation", value=explanation, inline=False)
            
            if adop_data.get('url'):
                embed.set_image(url=adop_data['url'])
            
            await interaction.followup.send(embed=embed)

        @self.tree.command(name="nasa", description="Searches NASA's image database")
        async def nasa(interaction: discord.Interaction, query: str):
            await interaction.response.defer(thinking=True)
            
            nasa_data = await self.api_manager.get_nasa_images(query)
            if isinstance(nasa_data, str):  # Error message
                await interaction.followup.send(nasa_data)
                return
            
            if not nasa_data or len(nasa_data) == 0:
                await interaction.followup.send(f"No NASA images found for query: {query}")
                return
            
            # Show first result
            first_result = nasa_data[0]
            embed = discord.Embed(title=first_result.get('title', 'NASA Image'), color=0x000080)
            embed.add_field(name="Date Created", value=first_result.get('date_created', 'Unknown'), inline=True)
            
            if first_result.get('description'):
                description = first_result['description']
                if len(description) > 1024:
                    description = description[:1021] + "..."
                embed.add_field(name="Description", value=description, inline=False)
            
            # Try to find an image URL
            links = first_result.get('links', [])
            image_url = None
            for link in links:
                if link.get('render') == 'image':
                    image_url = link.get('href')
                    break
            
            if image_url:
                embed.set_image(url=image_url)
            
            embed.set_footer(text=f"Showing 1 of {len(nasa_data)} results")
            
            await interaction.followup.send(embed=embed)

        @self.tree.command(name="valskin", description="Searches for Valorant weapon skins")
        async def valskin(interaction: discord.Interaction, skin_name: str):
            await interaction.response.defer(thinking=True)
            
            skins_data = await self.api_manager.get_valorant_skins()
            if isinstance(skins_data, str):  # Error message
                await interaction.followup.send(skins_data)
                return
            
            # Create ValorantSkin domain objects to fix Feature Envy
            matching_skins = []
            for skin_data in skins_data.get('data', []):
                skin = ValorantSkin(skin_data)
                if skin.matches_search(skin_name):
                    matching_skins.append(skin)
            
            if not matching_skins:
                await interaction.followup.send(f"No Valorant skins found matching: {skin_name}")
                return
            
            # Show first matching skin
            first_skin = matching_skins[0]
            embed = first_skin.create_embed()
            embed.set_footer(text=f"Showing 1 of {len(matching_skins)} matching skins")
            
            await interaction.followup.send(embed=embed) 