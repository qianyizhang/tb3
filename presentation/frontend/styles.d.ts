/** Vite scopes component styles and extracts them for the portable HTML builder. */
declare module '*.module.css' {
  const classes: Readonly<Record<string, string>>;
  export default classes;
}
