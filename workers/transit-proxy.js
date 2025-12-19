// Cloudflare Worker - Deploy at: https://dash.cloudflare.com/
// Set API_KEY as an environment variable/secret in Cloudflare dashboard

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    // CORS headers - allow cedar.ren and local development
    const origin = request.headers.get('Origin') || '*';
    const allowedOrigins = ['https://cedar.ren', 'http://localhost', 'http://127.0.0.1', 'null'];
    const allowOrigin = allowedOrigins.some(o => origin.startsWith(o)) ? origin : 'https://cedar.ren';

    const corsHeaders = {
      'Access-Control-Allow-Origin': allowOrigin,
      'Access-Control-Allow-Methods': 'GET, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    };

    // Handle preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders });
    }

    // Get parameters from request (default to Caltrain MTV)
    const agency = url.searchParams.get('agency') || 'CT';
    const stopCode = url.searchParams.get('stopCode') || '70212';

    // Build 511 API URL with secret key
    const apiUrl = new URL('https://api.511.org/transit/StopMonitoring');
    apiUrl.searchParams.set('api_key', env.API_KEY);
    apiUrl.searchParams.set('agency', agency);
    apiUrl.searchParams.set('format', 'json');
    if (stopCode) {
      apiUrl.searchParams.set('stopCode', stopCode);
    }

    try {
      const response = await fetch(apiUrl.toString());
      const data = await response.text();

      return new Response(data, {
        headers: {
          ...corsHeaders,
          'Content-Type': 'application/json',
        }
      });
    } catch (error) {
      return new Response(JSON.stringify({ error: error.message }), {
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });
    }
  }
};
