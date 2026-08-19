/**
 * Translates text using Google's public translation endpoint (no API key required).
 * Falls back to the original text if the request fails.
 */
export async function translateText(text: string, from: string, to: string = 'en'): Promise<string> {
  const trimmed = text.trim();
  if (!trimmed || from === to) return trimmed;

  try {
    const url = `https://translate.googleapis.com/translate_a/single?client=gtx&sl=${from}&tl=${to}&dt=t&q=${encodeURIComponent(
      trimmed
    )}`;
    const response = await fetch(url);
    const data = await response.json();
    const translated = data?.[0]?.map((chunk: [string]) => chunk[0]).join('') ?? trimmed;
    return translated;
  } catch (error) {
    console.error('Translation error:', error);
    return trimmed;
  }
}
