// Cloudflare Worker - Deploy at: https://dash.cloudflare.com/
// Set API_KEY as an environment variable/secret in Cloudflare dashboard

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    // CORS headers
    const corsHeaders = {
      'Access-Control-Allow-Origin': 'https://cedar.ren',
      'Access-Control-Allow-Methods': 'GET, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    };

    // Handle preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders });
    }

    // Get parameters from request
    const agency = url.searchParams.get('agency');
    const stopCode = url.searchParams.get('stopCode');

    if (!agency) {
      return new Response(JSON.stringify({ error: 'agency required' }), {
        status: 400,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });
    }

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
