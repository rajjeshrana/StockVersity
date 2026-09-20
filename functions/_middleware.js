export async function onRequest(context) {
    const incoming = new URL(context.request.url);

    // Keep the live Futures API proxy.
    if (incoming.pathname.startsWith("/api/futures")) {
        const target = new URL("https://api.stockversity.in");

        target.pathname = incoming.pathname;
        target.search = incoming.search;

        const request = new Request(target.toString(), context.request);
        return fetch(request);
    }

    // Serve the current Cloudflare Pages frontend/assets.
    return context.next();
}
