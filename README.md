## Matthew's Website

https://matthewjanssen.com

## Details
The site is built and rendered by [Hugo](https://gohugo.io/). Python scripts (written mostly with the help of [AI](https://kagi.com/assistant)) use [Bear's command-line tool](https://bear.app/faq/command-line-interface/) to extract relevant notes, then transform them into a format that Hugo can process. They're copied into the `content/` directory where Hugo uses them to build and render the site. The scripts can all be found in the `.build/` directory. I've also set up a launch daemon on my always-on Mac mini to execute the main script (which executes all the other ones) daily. This means the site should be updated daily with all the latest content.