# JinjaX Notes

[JinjaX documentation](https://jinjax.scaletti.dev/)

JinjaX is a component system built on top of Jinja2. It allows server-rendered templates to be organized and composed like UI components while remaining regular text templates.

## Core setup

```python
import jinjax
from fastapi import FastAPI
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")
templates.env.add_extension(jinjax.JinjaX)

catalog = jinjax.Catalog(jinja_env=templates.env)
catalog.add_folder("templates/components")
```

JinjaX should use the application's existing Jinja environment so custom filters, globals, loaders, and other configuration remain available.

## Components

Components are `.jinja` files stored inside folders registered with the catalog:

```text
components/
├── Card.jinja
├── Button.jinja
└── Person/
    └── Form.jinja
```

Component names are derived from their paths:

```text
Card.jinja         -> Card
Button.jinja       -> Button
Person/Form.jinja  -> Person.Form
```

They can be called from another template using XML-like syntax:

```jinja
<Card />
<Person.Form />

<Card>
  <p>Content supplied by the caller.</p>
</Card>
```

### Filename conventions

JinjaX supports either:

- PascalCase: `PersonForm.jinja`
- kebab-case: `person-form.jinja`

The resulting component name is still PascalCase (`person-form.jinja` becomes `PersonForm`). Do not mix PascalCase and kebab-case conventions within the same component library.

### Index components

A subfolder containing `index.jinja` can be called using only the folder name:

```text
components/
└── Tab/
    ├── index.jinja
    └── Panel.jinja
```

```text
Tab/index.jinja  -> Tab
Tab/Panel.jinja  -> Tab.Panel
```

## Component arguments

Arguments are declared at the top of a component with `{#def ... #}`:

```jinja
{#def action, method="post", multipart=False #}

<form
  method="{{ method }}"
  action="{{ action }}"
  {% if multipart %}enctype="multipart/form-data"{% endif %}
>
  {{ content }}
</form>
```

Arguments without defaults are required. Arguments with defaults are optional. Type annotations may be written, although they are not necessarily runtime validation:

```jinja
{#def
  data: dict[str, str],
  method: str = "post",
  multipart: bool = False
#}
```

String arguments:

```jinja
<Form action="/new" method="PATCH" />
<Card title="Hello world" type="big" />
```

Expression arguments can use Jinja-style or Vue-style syntax:

```jinja
<Example columns={{ 2 }} tabbed={{ False }} />
<Example :columns="2" :tabbed="False" />
```

Boolean attributes can use HTML-style syntax:

```jinja
<Example hidden />
```

Dashed argument names are converted to underscores, so `aria-label` corresponds to `aria_label`.

## Extra HTML attributes

Arguments not declared by the component are collected in an `attrs` object:

```jinja
{#def title #}

<div {{ attrs.render() }}>
  <h1>{{ title }}</h1>
  {{ content }}
</div>
```

Usage:

```jinja
<Card
  title="Products"
  class="Card--large"
  data-testid="products-card"
  open
>
  ...
</Card>
```

Useful methods include:

```jinja
{{ attrs.render() }}

{% do attrs.set(id="main-card") %}
{% do attrs.setdefault(aria_label="Products") %}
{% do attrs.add_class("active") %}
{% do attrs.prepend_class("important") %}
{% do attrs.remove_class("hidden") %}
{% set role = attrs.get("role", "region") %}
```

Class values are merged rather than blindly replaced. When forwarding attributes from one component to another, use `_attrs`:

```jinja
<InnerComponent _attrs={{ attrs }} />
```

Do not try to forward them by placing `{{ attrs.render() }}` directly inside the component invocation.

## Slots and content

The content between a component's opening and closing tags is passed through the implicit `content` variable:

```jinja
{# FancyButton.jinja #}
<button class="FancyButton">
  {{ content }}
</button>
```

Usage:

```jinja
<FancyButton>
  <i class="icon"></i>
  Save
</FancyButton>
```

The component controls the outer structure and styling while the caller supplies the inner content.

### Layout components

Slots are useful for layouts:

```jinja
{# Layout.jinja #}
{#def title #}

<!doctype html>
<html>
  <head>
    <title>{{ title }}</title>
  </head>
  <body>
    {{ content }}
  </body>
</html>
```

Usage:

```jinja
<Layout title="Archive">
  <main>...</main>
</Layout>
```

### Fallback content

A component can render fallback content when no content is supplied:

```jinja
<button type="submit">
  {% if content %}
    {{ content }}
  {% else %}
    Submit
  {% endif %}
</button>
```

A self-closing component receives an empty string as `content`.

### Named slots and composition

A component can request content by name using `content("header")`, `content("body")`, and so on. For complex components, composing separate child components is often clearer:

```jinja
<Modal>
  <ModalHeader>Confirm action</ModalHeader>
  <ModalBody>Are you sure?</ModalBody>
  <ModalFooter>
    <Button>Cancel</Button>
    <Button variant="danger">Confirm</Button>
  </ModalFooter>
</Modal>
```

To test a component in isolation, content can be supplied through `_content`:

```python
catalog.render("PageLayout", title="Test page", _content="TEST")
```

## Organization

Components can be organized using subfolders and called with dot-separated names:

```text
components/
├── common/
│   ├── Button.jinja
│   └── Form.jinja
├── user/
│   └── Avatar.jinja
└── layout/
    └── Page.jinja
```

```jinja
<common.Button />
<user.Avatar />
<layout.Page />
```

Multiple component folders can be registered. The first registered folder takes priority when components have the same name:

```python
catalog.add_folder("components/core")
catalog.add_folder("components/application")
```

Prefixes can provide namespaces for third-party component libraries:

```python
catalog.add_folder("third_party_components", prefix="ui")
```

## CSS and JavaScript assets

JinjaX can associate assets with individual components. Same-name assets may be discovered automatically:

```text
components/
├── Card.jinja
├── Card.css
└── Card.js
```

Assets can also be declared explicitly:

```jinja
{#css Card.css #}
{#js Card.js #}
```

Multiple assets can be declared with comma-separated paths:

```jinja
{#css reset.css, Card.css #}
{#js helpers.js, Card.js #}
```

The catalog collects assets used by the rendered component tree. A layout can emit them with:

```jinja
<head>
  {{ catalog.render_assets() }}
</head>
```

This allows pages to load only the assets needed by their components. The application still has to serve the referenced files.

## CSS scoping

JinjaX does not automatically scope CSS. This is global and unsafe:

```css
h1 {
  font-size: 2em;
}
```

Give the component a root class and scope its styles:

```jinja
<div class="Card">
  <h1>Card title</h1>
</div>
```

```css
.Card h1 {
  font-size: 2em;
}
```

Modern CSS nesting is equivalent:

```css
.Card {
  & h1 {
    font-size: 2em;
  }

  & a {
    color: blue;
  }
}
```

Use classes rather than IDs so a component can appear multiple times on a page.

## JinjaX and htmx

JinjaX and htmx operate at different layers:

- JinjaX composes server-rendered HTML.
- htmx sends requests and swaps returned HTML into the page.

A component can accept htmx attributes through `attrs`:

```jinja
{# Button.jinja #}
{#def label #}

<button {{ attrs.render(class="Button") }}>
  {{ label }}
  {{ content }}
</button>
```

Usage:

```jinja
<Button
  label="Delete"
  hx-delete="/users/42"
  hx-target="#user-row-42"
  hx-swap="outerHTML"
/>
```

JinjaX does not require a frontend runtime and does not replace htmx. It makes reusable htmx-enabled HTML easier to express.

Component JavaScript should account for dynamically inserted content. Event delegation is safer than binding listeners only during initial page load:

```javascript
document.addEventListener("click", (event) => {
  if (event.target.matches(".Card button.share")) {
    handleShare(event)
  }
})
```

## Middleware and serving assets

JinjaX includes middleware for serving component assets in some WSGI integrations. This is mainly relevant to Flask and other WSGI applications. ASGI frameworks may instead serve assets through their normal static-file mechanisms.

If component CSS, JavaScript, SVG, or image files are used, ensure the application exposes the corresponding directories and extensions.

## Example: a Card component

```jinja
{# Card.jinja #}
{#def title="", variant="default" #}
{#css Card.css #}

<article {{ attrs.render(class="Card Card--" ~ variant) }}>
  {% if title %}
    <header class="Card__header">
      <h2 class="Card__title">{{ title }}</h2>
    </header>
  {% endif %}

  <div class="Card__body">
    {{ content }}
  </div>
</article>
```

```css
.Card {
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  background: var(--surface-color);
}

.Card__header {
  padding: 1rem 1rem 0;
}

.Card__title {
  margin: 0;
}

.Card__body {
  padding: 1rem;
}

.Card--compact .Card__body {
  padding: 0.5rem;
}
```

## What JinjaX does not automatically provide

JinjaX does not automatically provide:

- runtime validation of component argument types
- static validation of all component usages
- CSS isolation
- accessibility validation
- htmx request handling
- CSRF protection
- frontend bundling or minification
- automatic asset hashing
- server-side `None` safety
- browser-side component lifecycle management

Those concerns still belong to the application, its test suite, or separate tooling.
