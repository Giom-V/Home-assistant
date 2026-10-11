import{t as e}from"./rolldown-runtime-B0Z9INg1.js";
/*
object-assign
(c) Sindre Sorhus
@license MIT
*/
var t=/* @__PURE__ */ e(((e,t)=>{var n=Object.getOwnPropertySymbols,r=Object.prototype.hasOwnProperty,i=Object.prototype.propertyIsEnumerable;function a(e){if(e==null)throw TypeError(`Object.assign cannot be called with null or undefined`);return Object(e)}function o(){try{if(!Object.assign)return!1;var e=/* @__PURE__ */ new String(`abc`);if(e[5]=`de`,Object.getOwnPropertyNames(e)[0]===`5`)return!1;for(var t={},n=0;n<10;n++)t[`_`+String.fromCharCode(n)]=n;if(Object.getOwnPropertyNames(t).map(function(e){return t[e]}).join(``)!==`0123456789`)return!1;var r={};return`abcdefghijklmnopqrst`.split(``).forEach(function(e){r[e]=e}),Object.keys(Object.assign({},r)).join(``)===`abcdefghijklmnopqrst`}catch{return!1}}t.exports=o()?Object.assign:function(e,t){for(var o,s=a(e),c,l=1;l<arguments.length;l++){for(var u in o=Object(arguments[l]),o)r.call(o,u)&&(s[u]=o[u]);if(n){c=n(o);for(var d=0;d<c.length;d++)i.call(o,c[d])&&(s[c[d]]=o[c[d]])}}return s}}));export{t};