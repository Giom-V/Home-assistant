/*! *****************************************************************************
Copyright (c) Microsoft Corporation.

Permission to use, copy, modify, and/or distribute this software for any
purpose with or without fee is hereby granted.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
PERFORMANCE OF THIS SOFTWARE.
***************************************************************************** */
function t(t,e,n,i){var s,r=arguments.length,o=r<3?e:null===i?i=Object.getOwnPropertyDescriptor(e,n):i;if("object"==typeof Reflect&&"function"==typeof Reflect.decorate)o=Reflect.decorate(t,e,n,i);else for(var a=t.length-1;a>=0;a--)(s=t[a])&&(o=(r<3?s(o):r>3?s(e,n,o):s(e,n))||o);return r>3&&o&&Object.defineProperty(e,n,o),o
/**
 * @license
 * Copyright (c) 2017 The Polymer Project Authors. All rights reserved.
 * This code may only be used under the BSD style license found at
 * http://polymer.github.io/LICENSE.txt
 * The complete set of authors may be found at
 * http://polymer.github.io/AUTHORS.txt
 * The complete set of contributors may be found at
 * http://polymer.github.io/CONTRIBUTORS.txt
 * Code distributed by Google as part of the polymer project is also
 * subject to an additional IP rights grant found at
 * http://polymer.github.io/PATENTS.txt
 */}const e="undefined"!=typeof window&&null!=window.customElements&&void 0!==window.customElements.polyfillWrapFlushCallback,n=(t,e,n=null)=>{for(;e!==n;){const n=e.nextSibling;t.removeChild(e),e=n}},i=`{{lit-${String(Math.random()).slice(2)}}}`,s=`\x3c!--${i}--\x3e`,r=new RegExp(`${i}|${s}`);class o{constructor(t,e){this.parts=[],this.element=e;const n=[],s=[],o=document.createTreeWalker(e.content,133,null,!1);let l=0,h=-1,p=0;const{strings:u,values:{length:m}}=t;for(;p<m;){const t=o.nextNode();if(null!==t){if(h++,1===t.nodeType){if(t.hasAttributes()){const e=t.attributes,{length:n}=e;let i=0;for(let t=0;t<n;t++)a(e[t].name,"$lit$")&&i++;for(;i-- >0;){const e=u[p],n=c.exec(e)[2],i=n.toLowerCase()+"$lit$",s=t.getAttribute(i);t.removeAttribute(i);const o=s.split(r);this.parts.push({type:"attribute",index:h,name:n,strings:o}),p+=o.length-1}}"TEMPLATE"===t.tagName&&(s.push(t),o.currentNode=t.content)}else if(3===t.nodeType){const e=t.data;if(e.indexOf(i)>=0){const i=t.parentNode,s=e.split(r),o=s.length-1;for(let e=0;e<o;e++){let n,r=s[e];if(""===r)n=d();else{const t=c.exec(r);null!==t&&a(t[2],"$lit$")&&(r=r.slice(0,t.index)+t[1]+t[2].slice(0,-"$lit$".length)+t[3]),n=document.createTextNode(r)}i.insertBefore(n,t),this.parts.push({type:"node",index:++h})}""===s[o]?(i.insertBefore(d(),t),n.push(t)):t.data=s[o],p+=o}}else if(8===t.nodeType)if(t.data===i){const e=t.parentNode;null!==t.previousSibling&&h!==l||(h++,e.insertBefore(d(),t)),l=h,this.parts.push({type:"node",index:h}),null===t.nextSibling?t.data="":(n.push(t),h--),p++}else{let e=-1;for(;-1!==(e=t.data.indexOf(i,e+1));)this.parts.push({type:"node",index:-1}),p++}}else o.currentNode=s.pop()}for(const t of n)t.parentNode.removeChild(t)}}const a=(t,e)=>{const n=t.length-e.length;return n>=0&&t.slice(n)===e},l=t=>-1!==t.index,d=()=>document.createComment(""),c=/([ \x09\x0a\x0c\x0d])([^\0-\x1F\x7F-\x9F "'>=/]+)([ \x09\x0a\x0c\x0d]*=[ \x09\x0a\x0c\x0d]*(?:[^ \x09\x0a\x0c\x0d"'`<>=]*|"[^"]*|'[^']*))$/;function h(t,e){const{element:{content:n},parts:i}=t,s=document.createTreeWalker(n,133,null,!1);let r=u(i),o=i[r],a=-1,l=0;const d=[];let c=null;for(;s.nextNode();){a++;const t=s.currentNode;for(t.previousSibling===c&&(c=null),e.has(t)&&(d.push(t),null===c&&(c=t)),null!==c&&l++;void 0!==o&&o.index===a;)o.index=null!==c?-1:o.index-l,r=u(i,r),o=i[r]}d.forEach(t=>t.parentNode.removeChild(t))}const p=t=>{let e=11===t.nodeType?0:1;const n=document.createTreeWalker(t,133,null,!1);for(;n.nextNode();)e++;return e},u=(t,e=-1)=>{for(let n=e+1;n<t.length;n++){const e=t[n];if(l(e))return n}return-1};
/**
 * @license
 * Copyright (c) 2017 The Polymer Project Authors. All rights reserved.
 * This code may only be used under the BSD style license found at
 * http://polymer.github.io/LICENSE.txt
 * The complete set of authors may be found at
 * http://polymer.github.io/AUTHORS.txt
 * The complete set of contributors may be found at
 * http://polymer.github.io/CONTRIBUTORS.txt
 * Code distributed by Google as part of the polymer project is also
 * subject to an additional IP rights grant found at
 * http://polymer.github.io/PATENTS.txt
 */
const m=new WeakMap,f=t=>(...e)=>{const n=t(...e);return m.set(n,!0),n},g=t=>"function"==typeof t&&m.has(t),y={},_={};
/**
 * @license
 * Copyright (c) 2017 The Polymer Project Authors. All rights reserved.
 * This code may only be used under the BSD style license found at
 * http://polymer.github.io/LICENSE.txt
 * The complete set of authors may be found at
 * http://polymer.github.io/AUTHORS.txt
 * The complete set of contributors may be found at
 * http://polymer.github.io/CONTRIBUTORS.txt
 * Code distributed by Google as part of the polymer project is also
 * subject to an additional IP rights grant found at
 * http://polymer.github.io/PATENTS.txt
 */
class v{constructor(t,e,n){this.__parts=[],this.template=t,this.processor=e,this.options=n}update(t){let e=0;for(const n of this.__parts)void 0!==n&&n.setValue(t[e]),e++;for(const t of this.__parts)void 0!==t&&t.commit()}_clone(){const t=e?this.template.element.content.cloneNode(!0):document.importNode(this.template.element.content,!0),n=[],i=this.template.parts,s=document.createTreeWalker(t,133,null,!1);let r,o=0,a=0,d=s.nextNode();for(;o<i.length;)if(r=i[o],l(r)){for(;a<r.index;)a++,"TEMPLATE"===d.nodeName&&(n.push(d),s.currentNode=d.content),null===(d=s.nextNode())&&(s.currentNode=n.pop(),d=s.nextNode());if("node"===r.type){const t=this.processor.handleTextExpression(this.options);t.insertAfterNode(d.previousSibling),this.__parts.push(t)}else this.__parts.push(...this.processor.handleAttributeExpressions(d,r.name,r.strings,this.options));o++}else this.__parts.push(void 0),o++;return e&&(document.adoptNode(t),customElements.upgrade(t)),t}}
/**
 * @license
 * Copyright (c) 2017 The Polymer Project Authors. All rights reserved.
 * This code may only be used under the BSD style license found at
 * http://polymer.github.io/LICENSE.txt
 * The complete set of authors may be found at
 * http://polymer.github.io/AUTHORS.txt
 * The complete set of contributors may be found at
 * http://polymer.github.io/CONTRIBUTORS.txt
 * Code distributed by Google as part of the polymer project is also
 * subject to an additional IP rights grant found at
 * http://polymer.github.io/PATENTS.txt
 */const w=window.trustedTypes&&trustedTypes.createPolicy("lit-html",{createHTML:t=>t}),S=` ${i} `;class b{constructor(t,e,n,i){this.strings=t,this.values=e,this.type=n,this.processor=i}getHTML(){const t=this.strings.length-1;let e="",n=!1;for(let r=0;r<t;r++){const t=this.strings[r],o=t.lastIndexOf("\x3c!--");n=(o>-1||n)&&-1===t.indexOf("--\x3e",o+1);const a=c.exec(t);e+=null===a?t+(n?S:s):t.substr(0,a.index)+a[1]+a[2]+"$lit$"+a[3]+i}return e+=this.strings[t],e}getTemplateElement(){const t=document.createElement("template");let e=this.getHTML();return void 0!==w&&(e=w.createHTML(e)),t.innerHTML=e,t}}
/**
 * @license
 * Copyright (c) 2017 The Polymer Project Authors. All rights reserved.
 * This code may only be used under the BSD style license found at
 * http://polymer.github.io/LICENSE.txt
 * The complete set of authors may be found at
 * http://polymer.github.io/AUTHORS.txt
 * The complete set of contributors may be found at
 * http://polymer.github.io/CONTRIBUTORS.txt
 * Code distributed by Google as part of the polymer project is also
 * subject to an additional IP rights grant found at
 * http://polymer.github.io/PATENTS.txt
 */const x=t=>null===t||!("object"==typeof t||"function"==typeof t),N=t=>Array.isArray(t)||!(!t||!t[Symbol.iterator]);class P{constructor(t,e,n){this.dirty=!0,this.element=t,this.name=e,this.strings=n,this.parts=[];for(let t=0;t<n.length-1;t++)this.parts[t]=this._createPart()}_createPart(){return new k(this)}_getValue(){const t=this.strings,e=t.length-1,n=this.parts;if(1===e&&""===t[0]&&""===t[1]){const t=n[0].value;if("symbol"==typeof t)return String(t);if("string"==typeof t||!N(t))return t}let i="";for(let s=0;s<e;s++){i+=t[s];const e=n[s];if(void 0!==e){const t=e.value;if(x(t)||!N(t))i+="string"==typeof t?t:String(t);else for(const e of t)i+="string"==typeof e?e:String(e)}}return i+=t[e],i}commit(){this.dirty&&(this.dirty=!1,this.element.setAttribute(this.name,this._getValue()))}}class k{constructor(t){this.value=void 0,this.committer=t}setValue(t){t===y||x(t)&&t===this.value||(this.value=t,g(t)||(this.committer.dirty=!0))}commit(){for(;g(this.value);){const t=this.value;this.value=y,t(this)}this.value!==y&&this.committer.commit()}}class C{constructor(t){this.value=void 0,this.__pendingValue=void 0,this.options=t}appendInto(t){this.startNode=t.appendChild(d()),this.endNode=t.appendChild(d())}insertAfterNode(t){this.startNode=t,this.endNode=t.nextSibling}appendIntoPart(t){t.__insert(this.startNode=d()),t.__insert(this.endNode=d())}insertAfterPart(t){t.__insert(this.startNode=d()),this.endNode=t.endNode,t.endNode=this.startNode}setValue(t){this.__pendingValue=t}commit(){if(null===this.startNode.parentNode)return;for(;g(this.__pendingValue);){const t=this.__pendingValue;this.__pendingValue=y,t(this)}const t=this.__pendingValue;t!==y&&(x(t)?t!==this.value&&this.__commitText(t):t instanceof b?this.__commitTemplateResult(t):t instanceof Node?this.__commitNode(t):N(t)?this.__commitIterable(t):t===_?(this.value=_,this.clear()):this.__commitText(t))}__insert(t){this.endNode.parentNode.insertBefore(t,this.endNode)}__commitNode(t){this.value!==t&&(this.clear(),this.__insert(t),this.value=t)}__commitText(t){const e=this.startNode.nextSibling,n="string"==typeof(t=null==t?"":t)?t:String(t);e===this.endNode.previousSibling&&3===e.nodeType?e.data=n:this.__commitNode(document.createTextNode(n)),this.value=t}__commitTemplateResult(t){const e=this.options.templateFactory(t);if(this.value instanceof v&&this.value.template===e)this.value.update(t.values);else{const n=new v(e,t.processor,this.options),i=n._clone();n.update(t.values),this.__commitNode(i),this.value=n}}__commitIterable(t){Array.isArray(this.value)||(this.value=[],this.clear());const e=this.value;let n,i=0;for(const s of t)n=e[i],void 0===n&&(n=new C(this.options),e.push(n),0===i?n.appendIntoPart(this):n.insertAfterPart(e[i-1])),n.setValue(s),n.commit(),i++;i<e.length&&(e.length=i,this.clear(n&&n.endNode))}clear(t=this.startNode){n(this.startNode.parentNode,t.nextSibling,this.endNode)}}class T{constructor(t,e,n){if(this.value=void 0,this.__pendingValue=void 0,2!==n.length||""!==n[0]||""!==n[1])throw new Error("Boolean attributes can only contain a single expression");this.element=t,this.name=e,this.strings=n}setValue(t){this.__pendingValue=t}commit(){for(;g(this.__pendingValue);){const t=this.__pendingValue;this.__pendingValue=y,t(this)}if(this.__pendingValue===y)return;const t=!!this.__pendingValue;this.value!==t&&(t?this.element.setAttribute(this.name,""):this.element.removeAttribute(this.name),this.value=t),this.__pendingValue=y}}class M extends P{constructor(t,e,n){super(t,e,n),this.single=2===n.length&&""===n[0]&&""===n[1]}_createPart(){return new E(this)}_getValue(){return this.single?this.parts[0].value:super._getValue()}commit(){this.dirty&&(this.dirty=!1,this.element[this.name]=this._getValue())}}class E extends k{}let A=!1;(()=>{try{const t={get capture(){return A=!0,!1}};window.addEventListener("test",t,t),window.removeEventListener("test",t,t)}catch(t){}})();class D{constructor(t,e,n){this.value=void 0,this.__pendingValue=void 0,this.element=t,this.eventName=e,this.eventContext=n,this.__boundHandleEvent=t=>this.handleEvent(t)}setValue(t){this.__pendingValue=t}commit(){for(;g(this.__pendingValue);){const t=this.__pendingValue;this.__pendingValue=y,t(this)}if(this.__pendingValue===y)return;const t=this.__pendingValue,e=this.value,n=null==t||null!=e&&(t.capture!==e.capture||t.once!==e.once||t.passive!==e.passive),i=null!=t&&(null==e||n);n&&this.element.removeEventListener(this.eventName,this.__boundHandleEvent,this.__options),i&&(this.__options=$(t),this.element.addEventListener(this.eventName,this.__boundHandleEvent,this.__options)),this.value=t,this.__pendingValue=y}handleEvent(t){"function"==typeof this.value?this.value.call(this.eventContext||this.element,t):this.value.handleEvent(t)}}const $=t=>t&&(A?{capture:t.capture,passive:t.passive,once:t.once}:t.capture)
/**
 * @license
 * Copyright (c) 2017 The Polymer Project Authors. All rights reserved.
 * This code may only be used under the BSD style license found at
 * http://polymer.github.io/LICENSE.txt
 * The complete set of authors may be found at
 * http://polymer.github.io/AUTHORS.txt
 * The complete set of contributors may be found at
 * http://polymer.github.io/CONTRIBUTORS.txt
 * Code distributed by Google as part of the polymer project is also
 * subject to an additional IP rights grant found at
 * http://polymer.github.io/PATENTS.txt
 */;function O(t){let e=V.get(t.type);void 0===e&&(e={stringsArray:new WeakMap,keyString:new Map},V.set(t.type,e));let n=e.stringsArray.get(t.strings);if(void 0!==n)return n;const s=t.strings.join(i);return n=e.keyString.get(s),void 0===n&&(n=new o(t,t.getTemplateElement()),e.keyString.set(s,n)),e.stringsArray.set(t.strings,n),n}const V=new Map,H=new WeakMap;
/**
 * @license
 * Copyright (c) 2017 The Polymer Project Authors. All rights reserved.
 * This code may only be used under the BSD style license found at
 * http://polymer.github.io/LICENSE.txt
 * The complete set of authors may be found at
 * http://polymer.github.io/AUTHORS.txt
 * The complete set of contributors may be found at
 * http://polymer.github.io/CONTRIBUTORS.txt
 * Code distributed by Google as part of the polymer project is also
 * subject to an additional IP rights grant found at
 * http://polymer.github.io/PATENTS.txt
 */const R=new
/**
 * @license
 * Copyright (c) 2017 The Polymer Project Authors. All rights reserved.
 * This code may only be used under the BSD style license found at
 * http://polymer.github.io/LICENSE.txt
 * The complete set of authors may be found at
 * http://polymer.github.io/AUTHORS.txt
 * The complete set of contributors may be found at
 * http://polymer.github.io/CONTRIBUTORS.txt
 * Code distributed by Google as part of the polymer project is also
 * subject to an additional IP rights grant found at
 * http://polymer.github.io/PATENTS.txt
 */
class{handleAttributeExpressions(t,e,n,i){const s=e[0];if("."===s){return new M(t,e.slice(1),n).parts}if("@"===s)return[new D(t,e.slice(1),i.eventContext)];if("?"===s)return[new T(t,e.slice(1),n)];return new P(t,e,n).parts}handleTextExpression(t){return new C(t)}};
/**
 * @license
 * Copyright (c) 2017 The Polymer Project Authors. All rights reserved.
 * This code may only be used under the BSD style license found at
 * http://polymer.github.io/LICENSE.txt
 * The complete set of authors may be found at
 * http://polymer.github.io/AUTHORS.txt
 * The complete set of contributors may be found at
 * http://polymer.github.io/CONTRIBUTORS.txt
 * Code distributed by Google as part of the polymer project is also
 * subject to an additional IP rights grant found at
 * http://polymer.github.io/PATENTS.txt
 */"undefined"!=typeof window&&(window.litHtmlVersions||(window.litHtmlVersions=[])).push("1.3.0");const U=(t,...e)=>new b(t,e,"html",R)
/**
 * @license
 * Copyright (c) 2017 The Polymer Project Authors. All rights reserved.
 * This code may only be used under the BSD style license found at
 * http://polymer.github.io/LICENSE.txt
 * The complete set of authors may be found at
 * http://polymer.github.io/AUTHORS.txt
 * The complete set of contributors may be found at
 * http://polymer.github.io/CONTRIBUTORS.txt
 * Code distributed by Google as part of the polymer project is also
 * subject to an additional IP rights grant found at
 * http://polymer.github.io/PATENTS.txt
 */,Y=(t,e)=>`${t}--${e}`;let L=!0;void 0===window.ShadyCSS?L=!1:void 0===window.ShadyCSS.prepareTemplateDom&&(console.warn("Incompatible ShadyCSS version detected. Please update to at least @webcomponents/webcomponentsjs@2.0.2 and @webcomponents/shadycss@1.3.1."),L=!1);const I=t=>e=>{const n=Y(e.type,t);let s=V.get(n);void 0===s&&(s={stringsArray:new WeakMap,keyString:new Map},V.set(n,s));let r=s.stringsArray.get(e.strings);if(void 0!==r)return r;const a=e.strings.join(i);if(r=s.keyString.get(a),void 0===r){const n=e.getTemplateElement();L&&window.ShadyCSS.prepareTemplateDom(n,t),r=new o(e,n),s.keyString.set(a,r)}return s.stringsArray.set(e.strings,r),r},j=["html","svg"],q=new Set,z=(t,e,n)=>{q.add(t);const i=n?n.element:document.createElement("template"),s=e.querySelectorAll("style"),{length:r}=s;if(0===r)return void window.ShadyCSS.prepareTemplateStyles(i,t);const o=document.createElement("style");for(let t=0;t<r;t++){const e=s[t];e.parentNode.removeChild(e),o.textContent+=e.textContent}(t=>{j.forEach(e=>{const n=V.get(Y(e,t));void 0!==n&&n.keyString.forEach(t=>{const{element:{content:e}}=t,n=new Set;Array.from(e.querySelectorAll("style")).forEach(t=>{n.add(t)}),h(t,n)})})})(t);const a=i.content;n?function(t,e,n=null){const{element:{content:i},parts:s}=t;if(null==n)return void i.appendChild(e);const r=document.createTreeWalker(i,133,null,!1);let o=u(s),a=0,l=-1;for(;r.nextNode();){l++;for(r.currentNode===n&&(a=p(e),n.parentNode.insertBefore(e,n));-1!==o&&s[o].index===l;){if(a>0){for(;-1!==o;)s[o].index+=a,o=u(s,o);return}o=u(s,o)}}}(n,o,a.firstChild):a.insertBefore(o,a.firstChild),window.ShadyCSS.prepareTemplateStyles(i,t);const l=a.querySelector("style");if(window.ShadyCSS.nativeShadow&&null!==l)e.insertBefore(l.cloneNode(!0),e.firstChild);else if(n){a.insertBefore(o,a.firstChild);const t=new Set;t.add(o),h(n,t)}};window.JSCompiler_renameProperty=(t,e)=>t;const F={toAttribute(t,e){switch(e){case Boolean:return t?"":null;case Object:case Array:return null==t?t:JSON.stringify(t)}return t},fromAttribute(t,e){switch(e){case Boolean:return null!==t;case Number:return null===t?null:Number(t);case Object:case Array:return JSON.parse(t)}return t}},B=(t,e)=>e!==t&&(e==e||t==t),W={attribute:!0,type:String,converter:F,reflect:!1,hasChanged:B};class J extends HTMLElement{constructor(){super(),this.initialize()}static get observedAttributes(){this.finalize();const t=[];return this._classProperties.forEach((e,n)=>{const i=this._attributeNameForProperty(n,e);void 0!==i&&(this._attributeToPropertyMap.set(i,n),t.push(i))}),t}static _ensureClassProperties(){if(!this.hasOwnProperty(JSCompiler_renameProperty("_classProperties",this))){this._classProperties=new Map;const t=Object.getPrototypeOf(this)._classProperties;void 0!==t&&t.forEach((t,e)=>this._classProperties.set(e,t))}}static createProperty(t,e=W){if(this._ensureClassProperties(),this._classProperties.set(t,e),e.noAccessor||this.prototype.hasOwnProperty(t))return;const n="symbol"==typeof t?Symbol():"__"+t,i=this.getPropertyDescriptor(t,n,e);void 0!==i&&Object.defineProperty(this.prototype,t,i)}static getPropertyDescriptor(t,e,n){return{get(){return this[e]},set(i){const s=this[t];this[e]=i,this.requestUpdateInternal(t,s,n)},configurable:!0,enumerable:!0}}static getPropertyOptions(t){return this._classProperties&&this._classProperties.get(t)||W}static finalize(){const t=Object.getPrototypeOf(this);if(t.hasOwnProperty("finalized")||t.finalize(),this.finalized=!0,this._ensureClassProperties(),this._attributeToPropertyMap=new Map,this.hasOwnProperty(JSCompiler_renameProperty("properties",this))){const t=this.properties,e=[...Object.getOwnPropertyNames(t),..."function"==typeof Object.getOwnPropertySymbols?Object.getOwnPropertySymbols(t):[]];for(const n of e)this.createProperty(n,t[n])}}static _attributeNameForProperty(t,e){const n=e.attribute;return!1===n?void 0:"string"==typeof n?n:"string"==typeof t?t.toLowerCase():void 0}static _valueHasChanged(t,e,n=B){return n(t,e)}static _propertyValueFromAttribute(t,e){const n=e.type,i=e.converter||F,s="function"==typeof i?i:i.fromAttribute;return s?s(t,n):t}static _propertyValueToAttribute(t,e){if(void 0===e.reflect)return;const n=e.type,i=e.converter;return(i&&i.toAttribute||F.toAttribute)(t,n)}initialize(){this._updateState=0,this._updatePromise=new Promise(t=>this._enableUpdatingResolver=t),this._changedProperties=new Map,this._saveInstanceProperties(),this.requestUpdateInternal()}_saveInstanceProperties(){this.constructor._classProperties.forEach((t,e)=>{if(this.hasOwnProperty(e)){const t=this[e];delete this[e],this._instanceProperties||(this._instanceProperties=new Map),this._instanceProperties.set(e,t)}})}_applyInstanceProperties(){this._instanceProperties.forEach((t,e)=>this[e]=t),this._instanceProperties=void 0}connectedCallback(){this.enableUpdating()}enableUpdating(){void 0!==this._enableUpdatingResolver&&(this._enableUpdatingResolver(),this._enableUpdatingResolver=void 0)}disconnectedCallback(){}attributeChangedCallback(t,e,n){e!==n&&this._attributeToProperty(t,n)}_propertyToAttribute(t,e,n=W){const i=this.constructor,s=i._attributeNameForProperty(t,n);if(void 0!==s){const t=i._propertyValueToAttribute(e,n);if(void 0===t)return;this._updateState=8|this._updateState,null==t?this.removeAttribute(s):this.setAttribute(s,t),this._updateState=-9&this._updateState}}_attributeToProperty(t,e){if(8&this._updateState)return;const n=this.constructor,i=n._attributeToPropertyMap.get(t);if(void 0!==i){const t=n.getPropertyOptions(i);this._updateState=16|this._updateState,this[i]=n._propertyValueFromAttribute(e,t),this._updateState=-17&this._updateState}}requestUpdateInternal(t,e,n){let i=!0;if(void 0!==t){const s=this.constructor;n=n||s.getPropertyOptions(t),s._valueHasChanged(this[t],e,n.hasChanged)?(this._changedProperties.has(t)||this._changedProperties.set(t,e),!0!==n.reflect||16&this._updateState||(void 0===this._reflectingProperties&&(this._reflectingProperties=new Map),this._reflectingProperties.set(t,n))):i=!1}!this._hasRequestedUpdate&&i&&(this._updatePromise=this._enqueueUpdate())}requestUpdate(t,e){return this.requestUpdateInternal(t,e),this.updateComplete}async _enqueueUpdate(){this._updateState=4|this._updateState;try{await this._updatePromise}catch(t){}const t=this.performUpdate();return null!=t&&await t,!this._hasRequestedUpdate}get _hasRequestedUpdate(){return 4&this._updateState}get hasUpdated(){return 1&this._updateState}performUpdate(){if(!this._hasRequestedUpdate)return;this._instanceProperties&&this._applyInstanceProperties();let t=!1;const e=this._changedProperties;try{t=this.shouldUpdate(e),t?this.update(e):this._markUpdated()}catch(e){throw t=!1,this._markUpdated(),e}t&&(1&this._updateState||(this._updateState=1|this._updateState,this.firstUpdated(e)),this.updated(e))}_markUpdated(){this._changedProperties=new Map,this._updateState=-5&this._updateState}get updateComplete(){return this._getUpdateComplete()}_getUpdateComplete(){return this._updatePromise}shouldUpdate(t){return!0}update(t){void 0!==this._reflectingProperties&&this._reflectingProperties.size>0&&(this._reflectingProperties.forEach((t,e)=>this._propertyToAttribute(e,this[e],t)),this._reflectingProperties=void 0),this._markUpdated()}updated(t){}firstUpdated(t){}}J.finalized=!0;
/**
 * @license
 * Copyright (c) 2017 The Polymer Project Authors. All rights reserved.
 * This code may only be used under the BSD style license found at
 * http://polymer.github.io/LICENSE.txt
 * The complete set of authors may be found at
 * http://polymer.github.io/AUTHORS.txt
 * The complete set of contributors may be found at
 * http://polymer.github.io/CONTRIBUTORS.txt
 * Code distributed by Google as part of the polymer project is also
 * subject to an additional IP rights grant found at
 * http://polymer.github.io/PATENTS.txt
 */
const Z=(t,e)=>"method"===e.kind&&e.descriptor&&!("value"in e.descriptor)?Object.assign(Object.assign({},e),{finisher(n){n.createProperty(e.key,t)}}):{kind:"field",key:Symbol(),placement:"own",descriptor:{},initializer(){"function"==typeof e.initializer&&(this[e.key]=e.initializer.call(this))},finisher(n){n.createProperty(e.key,t)}};function K(t){return(e,n)=>void 0!==n?((t,e,n)=>{e.constructor.createProperty(n,t)})(t,e,n):Z(t,e)}
/**
@license
Copyright (c) 2019 The Polymer Project Authors. All rights reserved.
This code may only be used under the BSD style license found at
http://polymer.github.io/LICENSE.txt The complete set of authors may be found at
http://polymer.github.io/AUTHORS.txt The complete set of contributors may be
found at http://polymer.github.io/CONTRIBUTORS.txt Code distributed by Google as
part of the polymer project is also subject to an additional IP rights grant
found at http://polymer.github.io/PATENTS.txt
*/const X=window.ShadowRoot&&(void 0===window.ShadyCSS||window.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,G=Symbol();class Q{constructor(t,e){if(e!==G)throw new Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t}get styleSheet(){return void 0===this._styleSheet&&(X?(this._styleSheet=new CSSStyleSheet,this._styleSheet.replaceSync(this.cssText)):this._styleSheet=null),this._styleSheet}toString(){return this.cssText}}const tt=(t,...e)=>{const n=e.reduce((e,n,i)=>e+(t=>{if(t instanceof Q)return t.cssText;if("number"==typeof t)return t;throw new Error(`Value passed to 'css' function must be a 'css' function result: ${t}. Use 'unsafeCSS' to pass non-literal values, but\n            take care to ensure page security.`)})(n)+t[i+1],t[0]);return new Q(n,G)};
/**
 * @license
 * Copyright (c) 2017 The Polymer Project Authors. All rights reserved.
 * This code may only be used under the BSD style license found at
 * http://polymer.github.io/LICENSE.txt
 * The complete set of authors may be found at
 * http://polymer.github.io/AUTHORS.txt
 * The complete set of contributors may be found at
 * http://polymer.github.io/CONTRIBUTORS.txt
 * Code distributed by Google as part of the polymer project is also
 * subject to an additional IP rights grant found at
 * http://polymer.github.io/PATENTS.txt
 */
(window.litElementVersions||(window.litElementVersions=[])).push("2.4.0");const et={};class nt extends J{static getStyles(){return this.styles}static _getUniqueStyles(){if(this.hasOwnProperty(JSCompiler_renameProperty("_styles",this)))return;const t=this.getStyles();if(Array.isArray(t)){const e=(t,n)=>t.reduceRight((t,n)=>Array.isArray(n)?e(n,t):(t.add(n),t),n),n=e(t,new Set),i=[];n.forEach(t=>i.unshift(t)),this._styles=i}else this._styles=void 0===t?[]:[t];this._styles=this._styles.map(t=>{if(t instanceof CSSStyleSheet&&!X){const e=Array.prototype.slice.call(t.cssRules).reduce((t,e)=>t+e.cssText,"");return new Q(String(e),G)}return t})}initialize(){super.initialize(),this.constructor._getUniqueStyles(),this.renderRoot=this.createRenderRoot(),window.ShadowRoot&&this.renderRoot instanceof window.ShadowRoot&&this.adoptStyles()}createRenderRoot(){return this.attachShadow({mode:"open"})}adoptStyles(){const t=this.constructor._styles;0!==t.length&&(void 0===window.ShadyCSS||window.ShadyCSS.nativeShadow?X?this.renderRoot.adoptedStyleSheets=t.map(t=>t instanceof CSSStyleSheet?t:t.styleSheet):this._needsShimAdoptedStyleSheets=!0:window.ShadyCSS.ScopingShim.prepareAdoptedCssText(t.map(t=>t.cssText),this.localName))}connectedCallback(){super.connectedCallback(),this.hasUpdated&&void 0!==window.ShadyCSS&&window.ShadyCSS.styleElement(this)}update(t){const e=this.render();super.update(t),e!==et&&this.constructor.render(e,this.renderRoot,{scopeName:this.localName,eventContext:this}),this._needsShimAdoptedStyleSheets&&(this._needsShimAdoptedStyleSheets=!1,this.constructor._styles.forEach(t=>{const e=document.createElement("style");e.textContent=t.cssText,this.renderRoot.appendChild(e)}))}render(){return et}}nt.finalized=!0,nt.render=(t,e,i)=>{if(!i||"object"!=typeof i||!i.scopeName)throw new Error("The `scopeName` option is required.");const s=i.scopeName,r=H.has(e),o=L&&11===e.nodeType&&!!e.host,a=o&&!q.has(s),l=a?document.createDocumentFragment():e;if(((t,e,i)=>{let s=H.get(e);void 0===s&&(n(e,e.firstChild),H.set(e,s=new C(Object.assign({templateFactory:O},i))),s.appendInto(e)),s.setValue(t),s.commit()})(t,l,Object.assign({templateFactory:I(s)},i)),a){const t=H.get(l);H.delete(l);const i=t.value instanceof v?t.value.template:void 0;z(s,l,i),n(e,e.firstChild),e.appendChild(l),H.set(e,t)}!r&&o&&window.ShadyCSS.styleElement(e.host)};
/**
 * @license
 * Copyright (c) 2017 The Polymer Project Authors. All rights reserved.
 * This code may only be used under the BSD style license found at
 * http://polymer.github.io/LICENSE.txt
 * The complete set of authors may be found at
 * http://polymer.github.io/AUTHORS.txt
 * The complete set of contributors may be found at
 * http://polymer.github.io/CONTRIBUTORS.txt
 * Code distributed by Google as part of the polymer project is also
 * subject to an additional IP rights grant found at
 * http://polymer.github.io/PATENTS.txt
 */
const it=(t,e)=>{const n=t.startNode.parentNode,i=void 0===e?t.endNode:e.startNode,s=n.insertBefore(d(),i);n.insertBefore(d(),i);const r=new C(t.options);return r.insertAfterNode(s),r},st=(t,e)=>(t.setValue(e),t.commit(),t),rt=(t,e,n)=>{const i=t.startNode.parentNode,s=n?n.startNode:t.endNode,r=e.endNode.nextSibling;r!==s&&((t,e,n=null,i=null)=>{for(;e!==n;){const n=e.nextSibling;t.insertBefore(e,i),e=n}})(i,e.startNode,r,s)},ot=t=>{n(t.startNode.parentNode,t.startNode,t.endNode.nextSibling)},at=(t,e,n)=>{const i=new Map;for(let s=e;s<=n;s++)i.set(t[s],s);return i},lt=new WeakMap,dt=new WeakMap,ct=f((t,e,n)=>{let i;return void 0===n?n=e:void 0!==e&&(i=e),e=>{if(!(e instanceof C))throw new Error("repeat can only be used in text bindings");const s=lt.get(e)||[],r=dt.get(e)||[],o=[],a=[],l=[];let d,c,h=0;for(const e of t)l[h]=i?i(e,h):h,a[h]=n(e,h),h++;let p=0,u=s.length-1,m=0,f=a.length-1;for(;p<=u&&m<=f;)if(null===s[p])p++;else if(null===s[u])u--;else if(r[p]===l[m])o[m]=st(s[p],a[m]),p++,m++;else if(r[u]===l[f])o[f]=st(s[u],a[f]),u--,f--;else if(r[p]===l[f])o[f]=st(s[p],a[f]),rt(e,s[p],o[f+1]),p++,f--;else if(r[u]===l[m])o[m]=st(s[u],a[m]),rt(e,s[u],s[p]),u--,m++;else if(void 0===d&&(d=at(l,m,f),c=at(r,p,u)),d.has(r[p]))if(d.has(r[u])){const t=c.get(l[m]),n=void 0!==t?s[t]:null;if(null===n){const t=it(e,s[p]);st(t,a[m]),o[m]=t}else o[m]=st(n,a[m]),rt(e,n,s[p]),s[t]=null;m++}else ot(s[u]),u--;else ot(s[p]),p++;for(;m<=f;){const t=it(e,o[f+1]);st(t,a[m]),o[m++]=t}for(;p<=u;){const t=s[p++];null!==t&&ot(t)}lt.set(e,o),dt.set(e,l)}});var ht=/d{1,4}|M{1,4}|YY(?:YY)?|S{1,3}|Do|ZZ|Z|([HhMsDm])\1?|[aA]|"[^"]*"|'[^']*'/g,pt="[^\\s]+",ut=/\[([^]*?)\]/gm;function mt(t,e){for(var n=[],i=0,s=t.length;i<s;i++)n.push(t[i].substr(0,e));return n}var ft=function(t){return function(e,n){var i=n[t].map((function(t){return t.toLowerCase()})).indexOf(e.toLowerCase());return i>-1?i:null}};function gt(t){for(var e=[],n=1;n<arguments.length;n++)e[n-1]=arguments[n];for(var i=0,s=e;i<s.length;i++){var r=s[i];for(var o in r)t[o]=r[o]}return t}var yt=["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"],_t=["January","February","March","April","May","June","July","August","September","October","November","December"],vt=mt(_t,3),wt={dayNamesShort:mt(yt,3),dayNames:yt,monthNamesShort:vt,monthNames:_t,amPm:["am","pm"],DoFn:function(t){return t+["th","st","nd","rd"][t%10>3?0:(t-t%10!=10?1:0)*t%10]}},St=gt({},wt),bt=function(t,e){for(void 0===e&&(e=2),t=String(t);t.length<e;)t="0"+t;return t},xt={D:function(t){return String(t.getDate())},DD:function(t){return bt(t.getDate())},Do:function(t,e){return e.DoFn(t.getDate())},d:function(t){return String(t.getDay())},dd:function(t){return bt(t.getDay())},ddd:function(t,e){return e.dayNamesShort[t.getDay()]},dddd:function(t,e){return e.dayNames[t.getDay()]},M:function(t){return String(t.getMonth()+1)},MM:function(t){return bt(t.getMonth()+1)},MMM:function(t,e){return e.monthNamesShort[t.getMonth()]},MMMM:function(t,e){return e.monthNames[t.getMonth()]},YY:function(t){return bt(String(t.getFullYear()),4).substr(2)},YYYY:function(t){return bt(t.getFullYear(),4)},h:function(t){return String(t.getHours()%12||12)},hh:function(t){return bt(t.getHours()%12||12)},H:function(t){return String(t.getHours())},HH:function(t){return bt(t.getHours())},m:function(t){return String(t.getMinutes())},mm:function(t){return bt(t.getMinutes())},s:function(t){return String(t.getSeconds())},ss:function(t){return bt(t.getSeconds())},S:function(t){return String(Math.round(t.getMilliseconds()/100))},SS:function(t){return bt(Math.round(t.getMilliseconds()/10),2)},SSS:function(t){return bt(t.getMilliseconds(),3)},a:function(t,e){return t.getHours()<12?e.amPm[0]:e.amPm[1]},A:function(t,e){return t.getHours()<12?e.amPm[0].toUpperCase():e.amPm[1].toUpperCase()},ZZ:function(t){var e=t.getTimezoneOffset();return(e>0?"-":"+")+bt(100*Math.floor(Math.abs(e)/60)+Math.abs(e)%60,4)},Z:function(t){var e=t.getTimezoneOffset();return(e>0?"-":"+")+bt(Math.floor(Math.abs(e)/60),2)+":"+bt(Math.abs(e)%60,2)}},Nt=function(t){return+t-1},Pt=[null,"[1-9]\\d?"],kt=[null,pt],Ct=["isPm",pt,function(t,e){var n=t.toLowerCase();return n===e.amPm[0]?0:n===e.amPm[1]?1:null}],Tt=["timezoneOffset","[^\\s]*?[\\+\\-]\\d\\d:?\\d\\d|[^\\s]*?Z?",function(t){var e=(t+"").match(/([+-]|\d\d)/gi);if(e){var n=60*+e[1]+parseInt(e[2],10);return"+"===e[0]?n:-n}return 0}],Mt=(ft("monthNamesShort"),ft("monthNames"),{default:"ddd MMM DD YYYY HH:mm:ss",shortDate:"M/D/YY",mediumDate:"MMM D, YYYY",longDate:"MMMM D, YYYY",fullDate:"dddd, MMMM D, YYYY",isoDate:"YYYY-MM-DD",isoDateTime:"YYYY-MM-DDTHH:mm:ssZ",shortTime:"HH:mm",mediumTime:"HH:mm:ss",longTime:"HH:mm:ss.SSS"});var Et=function(t,e,n){if(void 0===e&&(e=Mt.default),void 0===n&&(n={}),"number"==typeof t&&(t=new Date(t)),"[object Date]"!==Object.prototype.toString.call(t)||isNaN(t.getTime()))throw new Error("Invalid Date pass to format");var i=[];e=(e=Mt[e]||e).replace(ut,(function(t,e){return i.push(e),"@@@"}));var s=gt(gt({},St),n);return(e=e.replace(ht,(function(e){return xt[e](t,s)}))).replace(/@@@/g,(function(){return i.shift()}))},At=(function(){try{(new Date).toLocaleDateString("i")}catch(t){return"RangeError"===t.name}}(),function(){try{(new Date).toLocaleString("i")}catch(t){return"RangeError"===t.name}}(),function(){try{(new Date).toLocaleTimeString("i")}catch(t){return"RangeError"===t.name}}(),function(t,e,n,i){i=i||{},n=null==n?{}:n;var s=new Event(e,{bubbles:void 0===i.bubbles||i.bubbles,cancelable:Boolean(i.cancelable),composed:void 0===i.composed||i.composed});return s.detail=n,t.dispatchEvent(s),s}),Dt=function(t){At(window,"haptic",t)};const $t="ontouchstart"in window||navigator.maxTouchPoints>0||navigator.msMaxTouchPoints>0;class Ot extends HTMLElement{constructor(){super(),this.holdTime=500,this.ripple=document.createElement("mwc-ripple"),this.timer=void 0,this.held=!1,this.cooldownStart=!1,this.cooldownEnd=!1}connectedCallback(){Object.assign(this.style,{position:"absolute",width:$t?"100px":"50px",height:$t?"100px":"50px",transform:"translate(-50%, -50%)",pointerEvents:"none"}),this.appendChild(this.ripple),this.ripple.primary=!0,["touchcancel","mouseout","mouseup","touchmove","mousewheel","wheel","scroll"].forEach(t=>{document.addEventListener(t,()=>{clearTimeout(this.timer),this.stopAnimation(),this.timer=void 0},{passive:!0})})}bind(t,e){if(t.actionHandler)return;t.actionHandler=!0,t.addEventListener("contextmenu",t=>{const e=t||window.event;e.preventDefault&&e.preventDefault(),e.stopPropagation&&e.stopPropagation(),e.cancelBubble=!0,e.returnValue=!1});const n=t=>{if(this.cooldownStart)return;let e,n;this.held=!1,t.touches?(e=t.touches[0].pageX,n=t.touches[0].pageY):(e=t.pageX,n=t.pageY),this.timer=window.setTimeout(()=>{this.startAnimation(e,n),this.held=!0},this.holdTime),this.cooldownStart=!0,window.setTimeout(()=>this.cooldownStart=!1,100)},i=n=>{this.cooldownEnd||["touchend","touchcancel"].includes(n.type)&&void 0===this.timer||(clearTimeout(this.timer),this.stopAnimation(),this.timer=void 0,this.held?At(t,"action",{action:"hold"}):e.hasDoubleTap?1===n.detail||"keyup"===n.type?this.dblClickTimeout=window.setTimeout(()=>{At(t,"action",{action:"tap"})},250):(clearTimeout(this.dblClickTimeout),At(t,"action",{action:"double_tap"})):At(t,"action",{action:"tap"}),this.cooldownEnd=!0,window.setTimeout(()=>this.cooldownEnd=!1,100))};t.addEventListener("touchstart",n,{passive:!0}),t.addEventListener("touchend",i),t.addEventListener("touchcancel",i),t.addEventListener("keyup",t=>{if(13===t.keyCode)return i(t)});/iPhone OS 13_/.test(window.navigator.userAgent)||(t.addEventListener("mousedown",n,{passive:!0}),t.addEventListener("click",i))}startAnimation(t,e){Object.assign(this.style,{left:t+"px",top:e+"px",display:null}),this.ripple.disabled=!1,this.ripple.active=!0,this.ripple.unbounded=!0}stopAnimation(){this.ripple.active=!1,this.ripple.disabled=!0,this.style.display="none"}}customElements.define("action-handler-aftership",Ot);const Vt=(t,e)=>{const n=(()=>{const t=document.body;if(t.querySelector("action-handler-aftership"))return t.querySelector("action-handler-aftership");const e=document.createElement("action-handler-aftership");return t.appendChild(e),e})();n&&n.bind(t,e)},Ht=f((t={})=>e=>{Vt(e.committer.element,t)});console.info("%c  AFTERSHIP-CARD  \n%c  Version 1.2.2   ","color: orange; font-weight: bold; background: black","color: white; font-weight: bold; background: dimgray");let Rt=class extends nt{setConfig(t){if(!t||!t.entity)throw new Error("Invalid configuration");this._config=Object.assign({title:"Aftership"},t)}getCardSize(){return 6}shouldUpdate(t){if(t.has("_config"))return!0;if(this.hass&&this._config){const e=t.get("hass");if(e)return e.states[this._config.entity]!==this.hass.states[this._config.entity]}return!0}render(){if(!this._config||!this.hass)return U``;const t=this.hass.states[this._config.entity];if(!t)return U`
        <ha-card>
          <div class="warning">
            Entity not available: ${this._config.entity}
          </div>
        </ha-card>
      `;const e=t.attributes.trackings.filter((function(t){return"delivered"===t.status.toLowerCase()})),n=t.attributes.trackings.filter((function(t){return"delivered"!==t.status.toLowerCase()}));return U`
      <ha-card>
        <div class="header" @click=${this._moreInfo}>
          ${this._config.title}
        </div>
        ${ct(n,t=>t.tracking_number,(t,e)=>U`
              <paper-item>
                <paper-item-body class="icon">
                  <ha-icon
                    icon="mdi:truck-delivery"
                    .index=${e}
                    .item=${t}
                    .title="Expected Delivery: ${t.expected_delivery?new Date(t.expected_delivery).toDateString():"Unknown"}"
                    @action=${this._handleAction}
                    .actionHandler=${Ht({hasHold:!0})}
                  ></ha-icon>
                </paper-item-body>
                <paper-item-body>
                  <div>
                    ${t.name}
                  </div>
                  <div class="secondary">
                    ${t.last_checkpoint&&t.last_checkpoint.message?t.last_checkpoint.message:""}
                    (${t.status})
                  </div>
                </paper-item-body>
                <paper-item-body class="last">
                  <div style="text-transform: capitalize">
                    ${t.last_checkpoint&&t.last_checkpoint.location?t.last_checkpoint.location:t.status}
                  </div>
                  <div class="secondary">
                    ${new Date(t.last_update).toDateString()}
                  </div>
                </paper-item-body>
              </paper-item>
            `)}
        ${ct(e,t=>t.tracking_number,(t,e)=>U`
              <paper-item>
                <paper-item-body class="icon">
                  <ha-icon
                    icon="mdi:package"
                    .index=${e}
                    .item=${t}
                    @action=${this._handleAction}
                    .actionHandler=${Ht({hasHold:!0})}
                  ></ha-icon>
                </paper-item-body>
                <paper-item-body>
                  <div>
                    ${t.name}
                  </div>
                  <div class="secondary">
                    ${t.tracking_number} (${t.slug})
                  </div>
                </paper-item-body>
                <paper-item-body class="last">
                  <div>
                    ${t.status}
                  </div>
                  <div class="secondary">
                    ${new Date(t.last_update).toDateString()}
                  </div>
                </paper-item-body>
              </paper-item>
            `)}
        ${!1===this._config.show_add?0===e.length&&0===n.length?U`
                <paper-item>
                  Not tracking any packages right now
                </paper-item>
              `:null:U`
              <paper-item>
                <paper-item-body class="icon">
                  <ha-icon class="addButton" @click=${this._addItem} icon="hass:plus" title="Add Tracking"> </ha-icon>
                </paper-item-body>
                <paper-item-body>
                  <paper-input
                    no-label-float
                    placeholder="Title"
                    @keydown=${this._addKeyPress}
                    id="title"
                  ></paper-input>
                </paper-item-body>
                <paper-item-body>
                  <paper-input
                    no-label-float
                    placeholder="Tracking"
                    @keydown=${this._addKeyPress}
                    id="tracking"
                    required
                  ></paper-input>
                </paper-item-body>
                <paper-item-body>
                  <paper-input
                    no-label-float
                    placeholder="Slug"
                    @keydown=${this._addKeyPress}
                    id="slug"
                    required
                  ></paper-input>
                </paper-item-body>
              </paper-item>
            `}
      </ha-card>
    `}_daysUntilDelivery(t){const e=Math.floor((Date.parse(t)-(new Date).getMilliseconds())/864e5);return e+e>1?"days":"day"}get _title(){return this.shadowRoot?this.shadowRoot.querySelector("#title"):null}get _tracking(){return this.shadowRoot?this.shadowRoot.querySelector("#tracking"):null}get _slug(){return this.shadowRoot?this.shadowRoot.querySelector("#slug"):null}_addItem(t){const e=this._title,n=this._tracking,i=this._slug;this.hass&&e&&n&&n.value&&n.value.length>0&&(this.hass.callService("aftership","add_tracking",{tracking_number:n.value,title:e.value,slug:i.value}),e.value="",n.value="",i.value="",t&&e.focus())}_addKeyPress(t){13===t.keyCode&&this._addItem(null)}_removeItem(t){const e=t.target.item;window.confirm("Are you sure you want to remove this tracking?")&&(this.hass&&(this.hass.callService("aftership","remove_tracking",{tracking_number:e.tracking_number,slug:e.slug}),Dt("success")),Dt("failure"))}_moreInfo(){this._config&&At(this,"hass-more-info",{entityId:this._config.entity})}_handleAction(t){switch(t.detail.action){case"tap":this._openLink(t);break;case"hold":this._removeItem(t)}}_openLink(t){const e=t.target.item;window.open(e.link,"mywindow")}static get styles(){return tt`
      ha-card {
        padding: 16px;
      }

      .warning {
        display: block;
        color: black;
        background-color: #fce588;
        padding: 8px;
      }

      .header {
        /* start paper-font-headline style */
        font-family: 'Roboto', 'Noto', sans-serif;
        -webkit-font-smoothing: antialiased; /* OS X subpixel AA bleed bug */
        text-rendering: optimizeLegibility;
        font-size: 24px;
        font-weight: 400;
        letter-spacing: -0.012em;
        /* end paper-font-headline style */

        line-height: 40px;
        cursor: pointer;
      }

      paper-input {
        --paper-input-container-underline: {
          display: none;
        }
        --paper-input-container-underline-focus: {
          display: none;
        }
        --paper-input-container-underline-disabled: {
          display: none;
        }
        position: relative;
        top: 1px;
      }

      ha-icon {
        padding: 9px 15px 11px 15px;
        cursor: pointer;
        color: var(--primary-color);
      }

      .side-by-side {
        display: flex;
      }

      .side-by-side > * {
        flex: 1;
        padding-right: 4px;
      }

      paper-item {
        padding: 0;
      }

      paper-item-body {
        padding-right: 16px;
        margin-top: 16px;
        display: flex;
        flex-direction: column;
        justify-content: normal;
        flex: auto;
        flex-basis: auto;
        white-space: nowrap;
        overflow: hidden;
      }

      paper-item-body > * {
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }

      paper-item-body.icon {
        flex-direction: row;
        max-width: 54px;
        min-width: 54px;
      }

      table {
        width: 100%;
      }

      .last {
        text-align: right;
        min-width: 80px;
      }

      .secondary {
        display: block;
        color: var(--secondary-text-color);
        margin-top: -10px;
        font-size: 10px;
        white-space: nowrap;
      }

      table {
        margin-top: -16px;
      }

      #tracking {
        text-align: right;
      }

      .divider {
        height: 1px;
        background-color: var(--divider-color);
        margin: 6px 40px 6px 0px;
      }
    `}};var Ut;t([K()],Rt.prototype,"hass",void 0),t([K()],Rt.prototype,"_config",void 0),Rt=t([(Ut="aftership-card",t=>"function"==typeof t?((t,e)=>(window.customElements.define(t,e),e))(Ut,t):((t,e)=>{const{kind:n,elements:i}=e;return{kind:n,elements:i,finisher(e){window.customElements.define(t,e)}}})(Ut,t))],Rt);export{Rt as AftershipCard};
