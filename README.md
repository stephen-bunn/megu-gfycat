# Megu Gfycat

Megu plugin for fetching Gfycat media content.

At the moment this package includes the following plugins:

|Plugin       |Example URL                                                                  |
|-------------|-----------------------------------------------------------------------------|
|Gfycat Basic | https://gfycat.com/pepperyvictoriousgalah-wonder-woman-1984-i-like-to-party |

## Installation

With the latest version of `megu`, you should be able to install the plugin via `pip` using a command similar to the following:

```console
$ megu plugin add git+https://github.com/stephen-bunn/megu-gfycat.git
Installing Plugin $HOME/.config/megu/plugins
...
```

As always, this is still all heavily WIP.

## API vs. Guesswork

If you set the following configuration in your environment, the plugin will automatically attempt to utilize the Gfycat API intead of trying to do guesswork on what content can be extracted from the given URL.
The content the plugin extracts will contain a bunch more metadata and will be much more reliable than the guesswork solution that runs when the API logic is not enabled.

|Name                      |Description                                                                                     |
|--------------------------|------------------------------------------------------------------------------------------------|
|`MEGU_GFYCAT_API_ENABLED` |Case-insensitive, `1` or `true` is considered truthy. Otherwise the API logic is disabled.      |
|`MEGU_GFYCAT_API_TOKEN`   |The Client ID that Gfycat gives you when you sign as a developer.                               |
|`MEGU_GFYCAT_API_SECRET`  |The Client secret that Gfycat gives you when you sign as a developer.                           |

You can register for some API tokens at https://developers.gfycat.com/signup/#/.
