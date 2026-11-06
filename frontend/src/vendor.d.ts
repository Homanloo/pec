// plotly.js-basic-dist-min ships no types; this is the part of its API we use.
declare module "plotly.js-basic-dist-min" {
  const Plotly: {
    react(el: HTMLElement, data: object[], layout: object, config: object): Promise<unknown>;
    purge(el: HTMLElement): void;
  };
  export default Plotly;
}
