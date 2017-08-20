# GIT submodule instructions

Tutorial on how to use any submodule in any repository like here the [SimplifiedGmailApi](https://github.com/AnonymerNiklasistanonym/SendGmailSimplified).

(*If you want to learn more visit [this](https://github.com/blog/2104-working-with-submodules) site*)

## Joining a project using submodules

If you just clone the repository there will be an empty folder where the submodule is normally located.

To get it's content use either this at the `git clone` process:

```
git clone --recursive <project url>
```

Or if you already cloned the repository use:

```
git submodule update --init --recursive
```



Have fun programming! :smiley:



*PS: If you want to use this submodule do not forget to activate the API in the main project script*



## Bonus:

### Update the submodule

You used a newer version of the submodule and want to update the submodule link not only locally but on GitHub to this version:

```
git submodule update --remote --merge
```

Now the submodule file points to the current path the submodule is right now.

### Add a submodule

With this you can add a submodule yourself to a new directory of your current project:

```
git submodule add <project you want to use as submodule url> <directory name>
```