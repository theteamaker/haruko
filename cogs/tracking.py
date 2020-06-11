import aiohttp, asyncio, dateparser, datetime
from bs4 import BeautifulSoup as bs
from env import CANADAPOST_AUTHORIZATION
from discord.ext import commands
from discord import Embed, Colour

headers = {
    'Authorization': CANADAPOST_AUTHORIZATION,
    'Accept': 'application/vnd.cpc.track-v2+xml',
    'Accept-language': 'en-CA'
}

def setup(bot):
    bot.add_cog(Tracking(bot))

async def fetch(session, url):
    async with session.get(url, headers=headers) as response:
        return await response.text()

class TrackingEvent:
    def __init__(self, date, time, identifier, description, event_location, event_eta):
        self.date = date
        self.time = time
        self.identifier = identifier
        self.description = description
        self.event_location = event_location
        self.event_eta = event_eta

class Event:
    def __init__(self, tracking_number):
        self.tracking_number = tracking_number

    async def get_events(self):
        async with aiohttp.ClientSession() as session:
            html = await fetch(session, f'https://soa-gw.canadapost.ca/vis/track/pin/{self.tracking_number}/detail')
            content = bs(html, "lxml")
            tracking_events = content.find_all("occurrence")
            events = []

            if (eta := content.find("expected-delivery-date")) is not None and content.find("changed-expected-date") is None:
                package_eta = dateparser.parse(eta.text).strftime(r"%A, %B %d")
            elif content.find("expected-delivery-date") is not None and (eta := content.find("changed-expected-date")) is not None:
                package_eta = dateparser.parse(eta.text).strftime(r"%A, %B %d")
            else:
                package_eta = "Date Pending"

            for event in tracking_events:
                event_date = dateparser.parse(event.find("event-date").text).strftime(r"%A, %B %d")
                event_time = dateparser.parse(event.find("event-time").text).strftime(r"%I:%M%p")

                event_eta = package_eta
                event_identifier = event.find("event-identifier").text
                event_description = event.find("event-description").text

                if (city := event.find("event-site").text) != "" and (province := event.find("event-province").text) != "":
                    event_location = f"{city}, {province}"
                else:
                    event_location = ""
                
                tracking_event = TrackingEvent(
                    date = event_date,
                    time = event_time,
                    event_eta = event_eta,
                    identifier = event_identifier,
                    description = event_description,
                    event_location = event_location
                )
            
                events.append(tracking_event)

            return events
    
    async def get_latest_event(self):
        events = await self.get_events()
        return events[len(events) - 1]

class Tracking(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def track(self, ctx, *args):
        usage = "usage: `track <tracking_number>`"

        if len(args) != 1:
            await ctx.send(usage)
            return

        tracking_event = Event(args[0])
        events = await tracking_event.get_events()

        if len(events) == 0:
            await ctx.send("Not a valid tracking number!!! DIE!!!!")
            return

        sorted_events = {
        }

        dates = []

        for event in enumerate(events):
            if event[1].date not in dates:
                dates.append(event[1].date)
        
        for date in enumerate(dates):
            sorted_events[date[0]] = {0: date[1], 1: {}}
        
        for event in enumerate(events): # what have i done
            for sorted_event in sorted_events.items():
                if event[1].date == sorted_event[1][0]:
                    sorted_event[1][1][len(sorted_event[1][1])] = event[1]

        latest_eta = sorted_events[0][1][len(sorted_events[0][1]) - 1].event_eta

        embed = Embed(
            description=f"**Expected Delivery Date:** {latest_eta}",
            color=Colour(0xff0000)
        )

        for event_day in sorted_events.items():
            formatted_string = ""
            for event in event_day[1][1].items():
                to_concat = f"**{event[1].time}:** {event[1].description}"

                if event[1].event_location != "":
                    to_concat += f" **[**{event[1].event_location}**]**"
                
                formatted_string += f"{to_concat}\n"
            
            embed.add_field(
                name=event_day[1][0], 
                value=formatted_string, 
                inline=False
            )
            
        embed.set_author(
            name=f"Track: {tracking_event.tracking_number}", 
            url=f"https://www.canadapost.ca/trackweb/en#/search?searchFor={tracking_event.tracking_number}", 
            icon_url="https://lh3.googleusercontent.com/yRB0ZF7YBYq7yRnE3HtJ_ml5unM7etwknKEt8imuH9uqAVGjX3sfzwoK3YJNDIB33NE"
        )

        embed.set_footer(
            text="Information provided by Canada Post."
        )
        
        try:
            await ctx.send(embed=embed)
        except:
            await ctx.send("Something went wrong, and I'm not sure what.")