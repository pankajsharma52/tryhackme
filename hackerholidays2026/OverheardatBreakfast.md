Day 6 | Easy • OSINT • Social Media

The challenge started by analyzing the leaked conversation, which revealed the email address **[lambobytelotushotel@gmail.com](mailto:lambobytelotushotel@gmail.com)** and a hint that the profile service "started with a G." I used **Epieos** to investigate the email, which pointed me toward **Gravatar**. After locating the Gravatar profile, I found a **Profile URL** that led to the next stage of the challenge.

Opening the Profile URL revealed a **Base64-encoded** string. I decoded it using CyberChef, which revealed the final flag and completed the challenge.
