# TinyFeed
A lightweight, easy to use youtube channel & playlist feed aggregator

### Features
- Supports youtube channels and playlists
- Displays latest videos from added channels/playlists
- Ability to filter available videos by publishing date
- Search functionality for added channels and playlists
- Displays minimal video preview on hover over the video thumbnail
- Minimal, smooth interface
- Toggle between light and dark modes

### Dependencies
- Python 2.7 (pending update to python 3)
- Flask

### Usage
1. Clone the repository
2. In the main directory, create a folder named `store`
3. Navigate to `store` and create a file named `data.json`
4. Open `data.json` in a text editor and therein type `{}`
5. Save and exit the text editor
6. Double click `app.py` or run `python app.py flask run` in the terminal
7. Navigate to `localhost` or `127.0.0.1` on your web browser

### Adding channels/playlists
1. Extract the channel or playlist ID from its URL or page on youtube
2. Click `Add Channel` on the TinyFeed homepage and paste in the ID
3. Channel ID example: `UCtkZ7ARSt6LjifuTDkajT-g`
4. Playlist ID example: `PLF2KJ6Gy3cZ7jCgV1VEAIcr867nCkynPn`
5. Bookmarklet for extracting channel ID when it is not present in URL (navigate to the channel page before use):
```
javascript: for (var arrScripts = document.getElementsByTagName('script'), i = 0; i < arrScripts.length; i++) {if (arrScripts[i].textContent.indexOf('externalId') != -1) {var channelId = arrScripts[i].textContent.match(/\"externalId\"\s*\:\s*\"(.*?)\"/)[1];var channelTitle = document.title.match(/\(?\d*\)?\s?(.*?)\s\-\sYouTube/)[1];alert('The ID of the channel \'' + channelTitle + '\' is:\n\n' + channelId);break;}}
```

### Building
[Pyinstaller](https://www.pyinstaller.org/) may be used to build TinyFeed though this has not been tested yet. There are plans to release Windows and Linux binaries in the future.

### Limitations
All limitations resultant of the youtube channel and playlist rss/atom feed affect TinyFeed and may impede its proper functioning in certain cases.

### Credits
- Part of the app icon/favicon came from [svgrepo.com](https://www.svgrepo.com)
- Empty state icon made by [Freepik](https://www.freepik.com) from [www.flaticon.com](https://www.flaticon.com/)
- Xmltodict library by [martinblech](https://github.com/martinblech/xmltodict)

### Screenshots
![Light mode](https://i.imgur.com/8P9w1r5.png)

![Dark mode](https://i.imgur.com/FNCKMMJ.png)

### License
This project is released under the GPL-3.0 license. See the included license file.