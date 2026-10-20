#!/usr/bin/env node
// Strict network gate: never deploy when stable StudioNet RPC cannot verify 61999.
export const STABLE_RPC='https://studio.genlayer.com/api';
export const STABLE_CHAIN=61999;
export async function assertStudionet(){
  const response=await fetch(STABLE_RPC, {method:'POST',headers:{'content-type':'application/json'},
    body:JSON.stringify({jsonrpc:'2.0',id:61999,method:'eth_chainId',params:[]}),
    signal:AbortSignal.timeout(15000)});
  if(!response.ok)throw new Error(`RPC HTTP ${response.status}`);
  const body=await response.json();
  if(body?.error || typeof body.result!=='string' || !/^0x[0-9a-fA-F]+$/.test(body.result))
    throw new Error('Cannot verify StudioNet chain ID');
  const actual=Number.parseInt(body.result,16);
  if(actual!==STABLE_CHAIN)throw new Error(`Wrong chain: ${actual}, expected ${STABLE_CHAIN}`);
  console.log(`Confirmed stable studionet 61999 at ${STABLE_RPC}`);
  return actual;
}
if(process.argv[1]?.endsWith('assert_studionet.mjs')){
  assertStudionet().catch(e=>{console.error('DEPLOY REFUSED:',e.message);process.exitCode=1;});
}
