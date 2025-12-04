# AI Studio Guide: Publishing Private NPM Packages to GitHub Package Registry

This guide provides a comprehensive walkthrough for publishing private NPM packages to the GitHub Package Registry. Using GitHub Packages allows you to keep your code and packages in one place, simplifying permissions and integration with GitHub Actions.

## Prerequisites

-   A GitHub account with permissions to create packages in the target repository.
-   Node.js and npm installed on your local machine.
-   Your project checked out and a clean working directory.

## Step 1: Configure `package.json`

Your `package.json` file needs to be correctly configured to point to the GitHub Package Registry.

### 1.1 Package Scoping

GitHub Package Registry requires that npm packages be scoped to your GitHub username or organization. The `name` field in your `package.json` must be in the format `@OWNER/PACKAGE_NAME`.

For example, for the `mcp-server` package, the configuration is:

```json
"name": "@guillaumedescoteauxisabelle/stpb-mcp-server",
```

Where `guillaumedescoteauxisabelle` is the GitHub username/organization.

### 1.2 Repository URL

The `repository` field should point to the Git repository where your package's source code is located. This helps associate the package with its source.

```json
"repository": {
  "type": "git",
  "url": "https://github.com/jgwill/STPB.git",
  "directory": "mcp-server"
},
```

### 1.3 Publish Configuration (for private packages)

To ensure your package is published privately, you can either:

1.  **Rely on the repository's visibility**: If the GitHub repository is private, the package will be private by default.
2.  **Explicitly set `access`**: If you want to be explicit or if your repository is public but the package should be private, you would typically use a setting other than `"public"`. However, for GitHub packages, repository visibility is the primary controller. For clarity and to avoid accidental public publishing on npmjs.org, you can remove the `publishConfig` or ensure it's not set to public if the package is intended to be private.

For a private package, you can remove this block or set it to restricted, but for GitHub Packages, the repository's visibility is what matters.

```json
"publishConfig": {
  "access": "restricted"
}
```

## Step 2: Authenticate with GitHub Packages

You need to authenticate your npm client with GitHub Packages. This is done using a Personal Access Token (PAT).

### 2.1 Create a Personal Access Token (PAT)

1.  Go to your GitHub **Settings** > **Developer settings** > **Personal access tokens** > **Tokens (classic)**.
2.  Click **Generate new token** (or **Generate new token (classic)**).
3.  Give your token a descriptive name (e.g., `npm-publish`).
4.  Set the **Expiration** for the token.
5.  Select the following scopes:
    *   `write:packages` - Required to publish packages.
    *   `read:packages` - Required to install packages.
6.  Click **Generate token** and copy the token. **You will not see it again.**

### 2.2 Configure `.npmrc`

You need to configure npm to use the GitHub Package Registry for your scoped packages. You can do this at the project level (recommended) or user level.

**Project-level `.npmrc`:**

Create a file named `.npmrc` in the root of your project with the following content. Replace `OWNER` with your GitHub username or organization.

```
@OWNER:registry=https://npm.pkg.github.com/
//npm.pkg.github.com/:_authToken=${NODE_AUTH_TOKEN}
```

**Note:** Do not paste your PAT directly into this file. Instead, use an environment variable (`NODE_AUTH_TOKEN`).

Before publishing, set the environment variable in your terminal:

```bash
export NODE_AUTH_TOKEN=YOUR_PERSONAL_ACCESS_TOKEN
```

This prevents your secret token from being committed to source control.

## Step 3: Publish the Package

Once your `package.json` and `.npmrc` are configured and you've set your environment variable, you can publish the package.

1.  **Build your project**: Ensure your project is built and the distributable files are in the correct directory (e.g., `dist`). The `prepublishOnly` script in `package.json` should handle this.
    ```json
    "scripts": {
      "build": "tsc",
      "prepublishOnly": "npm run build"
    }
    ```
2.  **Publish**: Run the npm publish command.

    ```bash
    npm publish
    ```

If successful, you will see your package listed in the "Packages" section of your GitHub repository.

## Step 4: Installing the Private Package

To use your newly published private package in another project, you need to configure that project to authenticate with GitHub Packages as well.

1.  **Create a `.npmrc` file** in the consuming project's root, identical to the one you created for publishing:
    ```
    @OWNER:registry=https://npm.pkg.github.com/
    //npm.pkg.github.com/:_authToken=${NODE_AUTH_TOKEN}
    ```
2.  **Set the `NODE_AUTH_TOKEN` environment variable** in your terminal with a PAT that has `read:packages` scope.
3.  **Install the package**: You can now install the package using its scoped name.

    ```bash
    npm install @OWNER/PACKAGE_NAME
    ```
    For example:
    ```bash
    npm install @guillaumedescoteauxisabelle/stpb-mcp-server
    ```
