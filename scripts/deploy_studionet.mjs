#!/usr/bin/env node
import {spawnSync} from 'node:child_process';
import {existsSync,readFileSync} from 'node:fs';
import {resolve,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import readline from 'node:readline/promises';
import {stdin as input,stdout as output} from 'node:process';
import {assertStudionet} from './assert_studionet.mjs';

const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const cli=resolve(root,'node_modules','.bin',process.platform==='win32'?'genlayer.cmd':'genlayer');
const pkg=JSON.parse(readFileSync(resolve(root,'package.json'),'utf8'));
function run(args){
  const proc=spawnSync(cli,args,{cwd:root,encoding:'utf8',stdio:'inherit',shell:process.platform==='win32'});
  if(proc.status!==0)throw new Error(`Repository-local CLI failed: ${args.join(' ')}`);
}
async function main(){
  if(pkg.devDependencies?.genlayer!=='0.39.1')throw new Error('Exact local CLI pin modified');
  if(!existsSync(cli))throw new Error('Local CLI missing: run npm install first');
  const ver=spawnSync(cli,['--version'],{cwd:root,encoding:'utf8',shell:process.platform==='win32'});
  const v=(ver.stdout||'')+' '+(ver.stderr||'');
  if(ver.status!==0||!/(^|\D)0\.39\.1(\D|$)/.test(v))throw new Error(`Expected local CLI 0.39.1, got ${v.trim()}`);
  await assertStudionet();
  run(['network','set','studionet']);
  run(['network','info']);
  const rl=readline.createInterface({input,output});
  const answer=await rl.question('Type DEPLOY-61999 to deploy primary CourseLock: ');
  rl.close();
  if(answer.trim()!=='DEPLOY-61999')throw new Error('Canceled');
  run(['deploy','--contract','contracts/courselock.py']);
  console.log('Record address and finalized transaction receipt; do NOT infer finalization from submission.');
}
main().catch(e=>{console.error('DEPLOY REFUSED:',e.message);process.exitCode=1;});
