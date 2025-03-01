# SUSTech Venue Reserver

## 1. Why you should use a reserver

A reservation is typically from a phone or a computer, which launches a browser to complete. It costs much flow rate and higher load for the server. Hence, I developped this tool, pursuing the simplest way to book a ground efficiently and reduce the load on the server side.

It is available at 2025/03/01.

## 2. Requirements

To run the tool, you must have a Python environment. The library requirements are shown in the `requirements.txt`. It's recommended to use Python 3.10, which is the version that I used to develop this tool. Note that other popular Python versions may also be available, as I didn't conduct any version test.

It would be better if you are good at computer networks.

## 3. Theory for a reserver

Briefly, the path to make a reservation is:

- curl `https://open.weixin.qq.com/connect/oauth2/authorize?appid=CORPID&redirect_uri=REDIRECT_URI&response_type=code&scope=snsapi_base&state=STATE&agentid=AGENTID#wechat_redirect`
- be redirected to `https://reservation.sustech.edu.cn/clientMobile.html?code=CODE&state=STATE#/reservation/gym`
- get a user token by CODE indicated in the url above
- make a reservation based on the token

### (1) The first try to get access to the reservation system

To manually book a ground, we typically use Wechat or WeCom, then click the reservation button in the SUSTech Vene Reservation app and follow its instructions to complete the task. The first thing is, what happened when we click the "场地预约" button. If you click it, the app will launch a built-in browser, and you should choose a ground to book.

![](img/1-1.png)

![](img/1-2.png)

For the built-in browser, you can find a dots button at the top right side. If you click it, you can copy the url of the current page. And the url looks like `https://reservation.sustech.edu.cn/clientMobile.html?code=xxxxxxxxx&state=STATE#/reservation/gym`. However, if you use your default browser like Chrome to open it, you will fail due to the OAuth2 authentication and then be redirected to a new page whose url begins with `open.weixin.qq.com`.

Actually, once you click the "场地预约" button, the browser will open the url `https://open.weixin.qq.com/connect/oauth2/authorize?appid=CORPID&redirect_uri=REDIRECT_URI&response_type=code&scope=snsapi_base&state=STATE&agentid=AGENTID#wechat_redirect`. You can find something interesting through a careful review on the redirected url mentioned in the last paragraph. The url looks like `https://open.weixin.qq.com/connect/oauth2/authorize?appid=wx8839ace7048d181b&redirect_uri=https%3a%2f%2freservation.sustech.edu.cn%2fclientMobile.html%23%2freservation%2fgym&response_type=code&scope=snsapi_base&state=STATE&connect_redirect=1#wechat_redirect`, in which you can find the `appid`, `redirect_uri`, and some other parameters. For more information, please refer to the [document](https://developer.work.weixin.qq.com/document/path/96441) published by WeCom Developer Center.

That means, if you want to open the url in your default browser or in a Python script, you must find all of the required parameters mentioned in the WeCom document. Some parameters are easy to find, for example, we have already known that `CORPID` is `wx8839ace7048d181b` and `REDIRECT_URI` is `https%3a%2f%2freservation.sustech.edu.cn%2fclientMobile.html%23%2freservation%2fgym`. Once you complete all of them and open the completed url, you will be redirected to a link in form of `https://reservation.sustech.edu.cn/clientMobile.html?code=CODE&state=STATE#/reservation/gym`. **However, there is a parameter that I failed to find, `AGENTID`, which made me fail to be redirected. Furthermore, it means I failed to get the `CODE` shown in the redirected url, which would be quite important in the following steps. Basically, the administrators of SUSTech have the power to access it. If anyone is able to find it, please raise an issue, and your efforts will simplify the reserver quite much.**

As I failed to find such a `CODE`, I need to find another way.

### (2) Another way to access

Note that the built-in browser is able to fill the `AGENTID`, thus it is able to be redirected to a url contains a `CODE`. Maybe I can give up finding a `CODE` by myself, and just use the `CODE` indicated in the built-in browser.

Let's focus on what are done during a login to the reservation homepage, i.e., the HTTP requests and the responses. The reservation page uses TLSv1.3 to encrypt, and that means, if you use some tools like WireShark to grab the packets, it will be hard to retrieve the HTTP requests. It's recommended to use WireShark to try it out, then you will have a better understanding of what I wrote.

Hopefully, we can use the developer mode of WeCom to grab the HTTP requests. To enter the developer mode, please open the WeCom app and press Ctrl+Alt+Shift+D in windows or Command+Shift+Control+D in MacOS. The following instructions are based on MacOS, and you can do the same thing in Windows.

In the top bar, please follow the figure below to open the Web element inspection. Then right click the reservation page and choose "Inspect Element". Choose "Network" and "XHR/Fetch".

![](img/2-1.png)

![](img/2-2.png)

![](img/2-3.png)

You will find some requests, like `getAgreement`. Just choose one, and click "Headers" then scroll down to the bottom. There is a token that you should take down. Every request has the same token. If there is no token, just move on to another request. Note that the token will expire in about 5 minutes, so if you encounter an error named "鉴权失败2", please reload the page and use the new token.

![](img/2-4.png)

**Note that this token is very important, and we will use it in the following part.** Please keep in mind that we will encounter a new token in the captcha part, but the two tokens are not the same. I will use `tokenUser` and `tokenCaptcha` to tell them.

### (3) How to make a reservation

Based on the token, you can do anything use a script by sending a request as long as you can provided the right url and data. Note that a request contains three important parts, url, data, and header. To find what requests that you can send, you can click the buttons in the page and focus on the requests list shown in the element inspector window.

For example, we open the page shown below and focus on the `getOrderTimeConfigList` request.

![](img/3-1.png)

It means, if you send a request with

- url: `https://reservation.sustech.edu.cn/api/blade-app/qywx/getOrderTimeConfigList?groundId=1298272433186332673&startDate=2025-03-01&endDate=2025-03-07&userid=xxxxxxxx&token=xxxxxx`
- method: GET
- data: None
- header: something like `Accept`, `Accept-Encoding`, `Referer` and `User-Agent`

and you will get a response similar to the figure below.

![](img/3-2.png)

For those requests that have a data field, you can also check Request object tree in the same place.

You just need to write a Python script to send the request and catch the response, then you can print the text of the response and find anything you are interested in.

Now let's take a look at things happened in the procedure of a success reservation. You need to find a available ground and book it manually. Focus on the requests **in the time order**. After I booked a ground, the requests are shown in the figure below (but not in the time order).

![](img/3-3.png)

Ignore the process you find a free ground and focus on what happened from the time that you are right about to click the book button. A manual reservation process is that you click the book button, pass the captcha verification, then send a reservation request to the backend. Let's see the requests shown in the element inspector. In the table below, I emit the `https://reservation.sustech.edu.cn/api/` to simplify the Url part.

| Request Name |                       Url                       |                      Request Data                      | Response Data |                            Timing                            |             Operation              |
| :----------: | :---------------------------------------------: | :----------------------------------------------------: | :-----------: | :----------------------------------------------------------: | :--------------------------------: |
|     get      |                  `captcha/get`                  |            `captchaType`, `clientUid`, `ts`            |   `repData`   |            Once you enter the page to choose time            |     Ask for a captcha picture      |
|    check     |                 `captcha/check`                 |          `captchaType`, `pointJson`, `token`           |   `repData`   |            Once you finish a captcha verification            | Check if you pass the verification |
|     get      |                  `captcha/get`                  |            `captchaType`, `clientUid`, `ts`            |   `repData`   | Once you finish a captcha verification, the website would ask for a new captcha no matter if you passed or failed |     Ask for a captcha picture      |
|  saveOrder   | `blade-app/qywx/saveOrder?userid=xxx&token=xxx` | `captchaVerification`, `customerId`, `startTime`, etc. |    `data`     |       Once you pass the previous captcha verification        | Send a request to finish the order |

Hence, the idea to book a ground with a Python script is quite simple. You should follow this steps:

-   open a reservation page from your WeCom app and take down the `token` mentioned in (2), and regard it as `tokenUser`
-   send a POST request named get (**note that the request method should be POST but not GET**) with a fine-designed payload data which contains `captchaType`, `clientUid` and `ts`; the `captchaType` is always `blockPuzzle`, as you can find your own `clientUid` and `ts` by clicking the reservation button which will ask for a captcha
-   get the response data of get, and you should take down the `secretKey`, `token`, `jigsawImageBase64` and `originalImageBase64` for future usage; note that I will regard `tokenCaptcha` as the `token` found here
-   find the place that you should put the `jigsawImage` to and return the coordinates of the point
-   send a POST request named check with a data which contains `captchaType`, `pointJson` and `token`; you should find a proper way to convert the coordinates to the `pointJson` and put `tokenCaptcha` here
-   get the response data of check, and you will get `success: true` if you passed the captcha verification 
-   send a POST request named saveOrder with a data which contains many important things like `captchaVerification`; you can refer to my code to identify what you should write in the data, and you should find a way to construct the right `captchaVerification`
-   get the response data of saveOrder, and you will get `success: true` if you booked the ground successfully 

Now the problem is, given the `jigsawImage` and the `originalImage`, how we could find the proper point, pass the verification and get the right `captchaVerification`.

### (4) How to pass the captcha verification 

