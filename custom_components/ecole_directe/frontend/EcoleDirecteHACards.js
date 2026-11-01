var I=Object.getPrototypeOf(customElements.get("ha-panel-lovelace")),C=I.prototype.html,ze=I.prototype.css,B=class extends I{static get properties(){return{config:{},hass:{},header_title:{type:String},no_data_message:{type:String}}}getCardHeader(){let e=this.hass.states[this.config.entity].attributes;if(e){let t=typeof e.prenom=="string"&&e.prenom.length>0?e.prenom:e.nom_complet;return C`<div class="ed-card-header">
        ${this.header_title} ${t}
      </div>`}return C`<div class="ed-card-no-data">
      Veuillez choisir une autre entité
    </div>`}noDataMessage(){return C`<div class="ed-card-no-data">${this.no_data_message}</div>`}render(){return!this.config||!this.hass?C`<div class="ed-card-no-data">
        Veuillez configurer la carte
      </div>`:this.hass.states[this.config.entity]?(this.initCard(),C` <ha-card id="${this.config.entity}-card">
        ${this.config.display_header?this.getCardHeader():""}
        ${this.getCardContent()}
      </ha-card>`):C`<div class="ed-card-no-data">
      Veuillez choisir une autre entité
    </div>`}setConfig(e){if(!e.entity)throw new Error("Vous devez d\xE9finir une entit\xE9");this.config={...this.getDefaultConfig(),...e}}getItems(){let e=[],t=this.hass.states[this.config.entity];return t&&t.attributes[this.items_attribute_key]&&e.push(...t.attributes[this.items_attribute_key]),e}static get styles(){return ze`
      .ed-card-header {
        text-align: center;
      }
      div {
        padding: 12px;
        font-weight: bold;
        font-size: 1em;
      }
      .ed-card-no-data {
        display: block;
        padding: 8px;
        text-align: center;
        font-style: italic;
      }
    `}},_=B;var me=Object.getPrototypeOf(customElements.get("ha-panel-lovelace")),m=me.prototype.html,Be=me.prototype.css;Date.prototype.getWeekNumber=function(){var o=new Date(+this);return o.setHours(0,0,0,0),o.setDate(o.getDate()+4-(o.getDay()||7)),Math.ceil(((o-new Date(o.getFullYear(),0,1))/864e5+1)/7)};function Ie(o,e){return o.getFullYear()===e.getFullYear()&&o.getMonth()===e.getMonth()&&o.getDate()===e.getDate()}var V=class extends _{constructor(){super(...arguments);this.lunchBreakRendered=!1}initCard(){}getBreakRow(t,i){return m` <tr class="lunch-break ${i?"lesson-ended":""}">
      <td></td>
      <td><span></span></td>
      <td colspan="2">
        <span class="lesson-name">${t}</span>
      </td>
    </tr>`}getTimetableRow(t){let i=new Date().getTime(),a=Date.parse(t.start_at),s=Date.parse(t.end_at),n=m``;this.config.display_lunch_break&&t.is_afternoon&&!this.lunchBreakRendered&&(n=this.getBreakRow("Repas",this.config.dim_ended_lessons&&a<i),this.lunchBreakRendered=!0);let r=m`
      <tr
        class="${t.is_annule?"lesson-canceled":t.is_modifie?"lesson-modified":""} ${this.config.dim_ended_lessons&&s<i?"lesson-ended":""}"
      >
        <td>
          ${t.start_time}<br />
          ${t.end_time}
        </td>
        <td>
          <span style="background-color:${t.background_color}"></span>
        </td>
        <td>
          <span class="lesson-name">
            ${t.lesson}${t.remplace?m`<span class="lesson-replaced"> (remplace ${t.remplace})</span>`:""}
            ${t.is_modifie?m`<span class="lesson-modified-dot"></span>`:""}
          </span>
          ${this.config.display_classroom?m`<span class="lesson-classroom">
                ${t.salle?"Salle "+t.salle:""}
                ${t.salle&&this.config.display_teacher?", ":""}
              </span>`:""}
          ${this.config.display_teacher?m`<span class="lesson-teacher"> ${t.prof} </span>`:""}
        </td>
        <td>
          ${t.dispense?m`<span class="lesson-status">${t.dispense}</span>`:""}
        </td>
      </tr>
    `;return m`${n}${r}`}getFormattedDate(t){return new Date(t.start_at).toLocaleDateString("fr-FR",{weekday:"long",day:"2-digit",month:"2-digit"}).replace(/^(.)/,i=>i.toUpperCase())}getFormattedTime(t){return new Intl.DateTimeFormat("fr-FR",{hour:"numeric",minute:"numeric"}).format(new Date(t))}getDayHeader(t,i,a,s){return m`<div class="ed-timetable-header">
      ${this.config.enable_slider?m`<span
            class="ed-timetable-header-arrow-left ${s===0?"disabled":""}"
            @click=${n=>this.changeDay("previous",n)}
            >←</span
          >`:""}
      <span class="ed-timetable-header-date"
        >${this.getFormattedDate(t)}</span
      >
      ${this.config.display_day_hours&&i&&a?m`<span class="ed-timetable-header-hours">
            ${this.getFormattedTime(i)} -
            ${this.getFormattedTime(a)}
          </span>`:""}
      ${this.config.enable_slider?m`<span
            class="ed-timetable-header-arrow-right"
            @click=${n=>this.changeDay("next",n)}
            >→</span
          >`:""}
    </div>`}changeDay(t,i){if(i.preventDefault(),i.target.classList.contains("disabled"))return;let a=i.target.parentElement.parentElement,s=a.previousElementSibling&&a.previousElementSibling.classList.contains("ed-timetable-day-wrapper"),n=a.nextElementSibling&&a.nextElementSibling.classList.contains("ed-timetable-day-wrapper"),r=null;t==="previous"&&s?r=a.previousElementSibling:t==="next"&&n&&(r=a.nextElementSibling),r&&(a.classList.remove("active"),r.classList.add("active"),s=r.previousElementSibling&&r.previousElementSibling.classList.contains("ed-timetable-day-wrapper"),n=r.nextElementSibling&&r.nextElementSibling.classList.contains("ed-timetable-day-wrapper"),s||r.querySelector(".ed-timetable-header-arrow-left").classList.add("disabled"),n||r.querySelector(".ed-timetable-header-arrow-right").classList.add("disabled"))}render(){if(!this.config||!this.hass)return m`<div class="ed-card-no-data">
        Veuillez configurer la carte
      </div>`;let t=this.hass.states[this.config.entity];if(t){let i=t.attributes["Emploi du temps"];if(i){if(i.length>0&&i[0].stored_in_store){let d=i[0].store_key;if(this._storedData&&this._storedData[d])i=this._storedData[d];else return this._fetchingKeys||(this._fetchingKeys={}),this._fetchingKeys[d]||(this._fetchingKeys[d]=!0,this.hass.callWS({type:"ecole_directe/get_stored_data",key:d}).then(h=>{this._storedData||(this._storedData={}),this._storedData[d]=h.data||[],this.requestUpdate()}).catch(h=>{console.error("Error fetching stored data for key",d,h)})),m`<div class="ed-card-no-data">Chargement de l'emploi du temps...</div>`}this.lunchBreakRendered=!1;let a=[],s=[],n=0,r=null,l=null,p=new Date,u=0;for(let d=0;d<i.length;d++){let h=i[d],y=this.getFormattedDate(h),x=new Date(h.end_at);if(h.isAnnule||(r===null&&(r=h.start_at),l=h.end_at),h.isAnnule&&d<i.length-1){let P=i[d+1];if(h.start_at===P.start_at&&!P.isAnnule)continue}if(s.push(this.getTimetableRow(h)),d+1>=i.length||d+1<i.length&&y!==this.getFormattedDate(i[d+1]))this.config.enable_slider&&this.config.switch_to_next_day&&Ie(x,p)&&x<p&&(u=n+1),a.push(m`
              <div
                class="${this.config.enable_slider?"slider-enabled":""} ed-timetable-day-wrapper ${n===u?"active":""}"
              >
                ${this.getDayHeader(h,r,l,n)}
                <table>
                  ${s}
                </table>
              </div>
            `),s=[],this.lunchBreakRendered=!1,r=null,l=null,n++;else if(this.config.display_free_time_slots&&d+1<i.length){let P=new Date(h.end_at),ue=i[d+1],ge=new Date(ue.start_at);if(h.is_morning===ue.is_morning&&Math.floor((ge-P)/1e3/60)>30){let Ue=new Date;s.push(this.getBreakRow("Pas de cours",this.config.dim_ended_lessons&&ge<Ue))}}}return s.length>0&&a.push(m`<table>
              ${s}
            </table>`),m` <ha-card
          id="${this.config.entity}-card"
          class="${this.config.enable_slider?"ed-timetable-card-slider":""}"
        >
          ${this.config.display_header?this.getCardHeader():""}
          ${a}
        </ha-card>`}}return m`<div class="ed-card-no-data">
      Veuillez choisir une autre entité
    </div>`}setConfig(t){if(!t.entity)throw new Error("Vous devez d\xE9finir une entit\xE9");let i={entity:null,display_header:!0,display_classroom:!0,display_teacher:!0,display_day_hours:!0,display_lunch_break:!0,dim_ended_lessons:!0,enable_slider:!1,switch_to_next_day:!1,display_free_time_slots:!0};this.config={...i,...t},this.header_title="Emploi du temps de ",this.no_data_message="Pas d'emploi du temps \xE0 afficher"}static get styles(){return Be`
      ${super.styles}
      .ed-timetable-card-slider .ed-timetable-day-wrapper {
        display: none;
      }
      .ed-timetable-card-slider .ed-timetable-day-wrapper.active {
        display: block;
      }
      .ed-timetable-card-slider .ed-timetable-header-date {
        display: inline-block;
        text-align: center;
        width: 120px;
      }
      .ed-timetable-header-arrow-left,
      .ed-timetable-header-arrow-right {
        cursor: pointer;
      }
      .ed-timetable-header-arrow-left.disabled,
      .ed-timetable-header-arrow-right.disabled {
        opacity: 0.3;
        pointer-events: none;
      }
      span.ed-timetable-header-hours {
        float: right;
      }
      table {
        clear: both;
        font-size: 0.9em;
        font-family: Roboto;
        width: 100%;
        outline: 0px solid #393c3d;
        border-collapse: collapse;
      }
      tr:nth-child(odd) {
        background-color: rgba(0, 0, 0, 0.1);
      }
      td {
        vertical-align: middle;
        padding: 5px 10px 5px 10px;
        text-align: left;
      }
      tr td:first-child {
        width: 13%;
        text-align: right;
      }
      span.lesson-name {
        font-weight: bold;
        display: block;
      }
      tr td:nth-child(2) {
        width: 4px;
        padding: 5px 0;
      }
      tr td:nth-child(2) > span {
        display: inline-block;
        width: 4px;
        height: 3rem;
        border-radius: 4px;
        background-color: grey;
        margin-top: 4px;
      }
      span.lesson-status {
        color: white;
        background-color: rgb(75, 197, 253);
        padding: 4px;
        border-radius: 4px;
      }
      .lesson-canceled span.lesson-name {
        text-decoration: line-through;
      }
      .lesson-canceled span.lesson-status {
        background-color: rgb(250, 50, 75);
      }
      .lesson-modified span.lesson-name {
        font-style: italic;
      }
      .lesson-modified-dot {
        display: inline-block;
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background-color: orange;
        margin-left: 6px;
        vertical-align: middle;
      }
      .lesson-replaced {
        font-size: 0.85em;
        font-style: italic;
        opacity: 0.7;
      }
      .lesson-ended {
        opacity: 0.3;
      }
      div:not(.slider-enabled).ed-timetable-day-wrapper
        + div:not(.slider-enabled).ed-timetable-day-wrapper {
        border-top: 1px solid white;
      }
    `}static getStubConfig(){return{display_header:!0,display_lunch_break:!0,display_classroom:!0,display_teacher:!0,display_day_hours:!0,dim_ended_lessons:!0,enable_slider:!1,display_free_time_slots:!0,switch_to_next_day:!1}}static getConfigElement(){return document.createElement("ecole_directe-emploi_temps-card-editor")}};customElements.define("ecole_directe-emploi_temps-card",V);window.customCards=window.customCards||[];window.customCards.push({type:"ecole_directe-emploi_temps-card",name:"Carte de l'emploi du temps pour Ecole Directe",description:"Affiche l'emploi du temps pour Ecole Directe",documentationURL:"https://github.com/hacf-fr/EcoleDirecteHACards?tab=readme-ov-file#emploi_temps"});var T=globalThis,_e=o=>o,N=T.trustedTypes,fe=N?N.createPolicy("lit-html",{createHTML:o=>o}):void 0,xe="$lit$",$=`lit$${Math.random().toFixed(9).slice(2)}$`,Ae="?"+$,Ve=`<${Ae}>`,D=document,q=()=>D.createComment(""),O=o=>o===null||typeof o!="object"&&typeof o!="function",J=Array.isArray,Ke=o=>J(o)||typeof o?.[Symbol.iterator]=="function",K=`[ 	
\f\r]`,L=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,ye=/-->/g,ve=/>/g,A=RegExp(`>|${K}(?:([^\\s"'>=/]+)(${K}*=${K}*(?:[^ 	
\f\r"'\`<>=]|("|')|))|$)`,"g"),be=/'/g,$e=/"/g,Ee=/^(?:script|style|textarea|title)$/i,Q=o=>(e,...t)=>({_$litType$:o,strings:e,values:t}),pt=Q(1),ht=Q(2),ut=Q(3),k=Symbol.for("lit-noChange"),g=Symbol.for("lit-nothing"),we=new WeakMap,E=D.createTreeWalker(D,129);function De(o,e){if(!J(o)||!o.hasOwnProperty("raw"))throw Error("invalid template strings array");return fe!==void 0?fe.createHTML(e):e}var We=(o,e)=>{let t=o.length-1,i=[],a,s=e===2?"<svg>":e===3?"<math>":"",n=L;for(let r=0;r<t;r++){let l=o[r],p,u,d=-1,h=0;for(;h<l.length&&(n.lastIndex=h,u=n.exec(l),u!==null);)h=n.lastIndex,n===L?u[1]==="!--"?n=ye:u[1]!==void 0?n=ve:u[2]!==void 0?(Ee.test(u[2])&&(a=RegExp("</"+u[2],"g")),n=A):u[3]!==void 0&&(n=A):n===A?u[0]===">"?(n=a??L,d=-1):u[1]===void 0?d=-2:(d=n.lastIndex-u[2].length,p=u[1],n=u[3]===void 0?A:u[3]==='"'?$e:be):n===$e||n===be?n=A:n===ye||n===ve?n=L:(n=A,a=void 0);let y=n===A&&o[r+1].startsWith("/>")?" ":"";s+=n===L?l+Ve:d>=0?(i.push(p),l.slice(0,d)+xe+l.slice(d)+$+y):l+$+(d===-2?r:y)}return[De(o,s+(o[t]||"<?>")+(e===2?"</svg>":e===3?"</math>":"")),i]},H=class o{constructor({strings:e,_$litType$:t},i){let a;this.parts=[];let s=0,n=0,r=e.length-1,l=this.parts,[p,u]=We(e,t);if(this.el=o.createElement(p,i),E.currentNode=this.el.content,t===2||t===3){let d=this.el.content.firstChild;d.replaceWith(...d.childNodes)}for(;(a=E.nextNode())!==null&&l.length<r;){if(a.nodeType===1){if(a.hasAttributes())for(let d of a.getAttributeNames())if(d.endsWith(xe)){let h=u[n++],y=a.getAttribute(d).split($),x=/([.?@])?(.*)/.exec(h);l.push({type:1,index:s,name:x[2],strings:y,ctor:x[1]==="."?Y:x[1]==="?"?G:x[1]==="@"?X:F}),a.removeAttribute(d)}else d.startsWith($)&&(l.push({type:6,index:s}),a.removeAttribute(d));if(Ee.test(a.tagName)){let d=a.textContent.split($),h=d.length-1;if(h>0){a.textContent=N?N.emptyScript:"";for(let y=0;y<h;y++)a.append(d[y],q()),E.nextNode(),l.push({type:2,index:++s});a.append(d[h],q())}}}else if(a.nodeType===8)if(a.data===Ae)l.push({type:2,index:s});else{let d=-1;for(;(d=a.data.indexOf($,d+1))!==-1;)l.push({type:7,index:s}),d+=$.length-1}s++}}static createElement(e,t){let i=D.createElement("template");return i.innerHTML=e,i}};function S(o,e,t=o,i){if(e===k)return e;let a=i!==void 0?t._$Co?.[i]:t._$Cl,s=O(e)?void 0:e._$litDirective$;return a?.constructor!==s&&(a?._$AO?.(!1),s===void 0?a=void 0:(a=new s(o),a._$AT(o,t,i)),i!==void 0?(t._$Co??(t._$Co=[]))[i]=a:t._$Cl=a),a!==void 0&&(e=S(o,a._$AS(o,e.values),a,i)),e}var W=class{constructor(e,t){this._$AV=[],this._$AN=void 0,this._$AD=e,this._$AM=t}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(e){let{el:{content:t},parts:i}=this._$AD,a=(e?.creationScope??D).importNode(t,!0);E.currentNode=a;let s=E.nextNode(),n=0,r=0,l=i[0];for(;l!==void 0;){if(n===l.index){let p;l.type===2?p=new U(s,s.nextSibling,this,e):l.type===1?p=new l.ctor(s,l.name,l.strings,this,e):l.type===6&&(p=new Z(s,this,e)),this._$AV.push(p),l=i[++r]}n!==l?.index&&(s=E.nextNode(),n++)}return E.currentNode=D,a}p(e){let t=0;for(let i of this._$AV)i!==void 0&&(i.strings!==void 0?(i._$AI(e,i,t),t+=i.strings.length-2):i._$AI(e[t])),t++}},U=class o{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(e,t,i,a){this.type=2,this._$AH=g,this._$AN=void 0,this._$AA=e,this._$AB=t,this._$AM=i,this.options=a,this._$Cv=a?.isConnected??!0}get parentNode(){let e=this._$AA.parentNode,t=this._$AM;return t!==void 0&&e?.nodeType===11&&(e=t.parentNode),e}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(e,t=this){e=S(this,e,t),O(e)?e===g||e==null||e===""?(this._$AH!==g&&this._$AR(),this._$AH=g):e!==this._$AH&&e!==k&&this._(e):e._$litType$!==void 0?this.$(e):e.nodeType!==void 0?this.T(e):Ke(e)?this.k(e):this._(e)}O(e){return this._$AA.parentNode.insertBefore(e,this._$AB)}T(e){this._$AH!==e&&(this._$AR(),this._$AH=this.O(e))}_(e){this._$AH!==g&&O(this._$AH)?this._$AA.nextSibling.data=e:this.T(D.createTextNode(e)),this._$AH=e}$(e){let{values:t,_$litType$:i}=e,a=typeof i=="number"?this._$AC(e):(i.el===void 0&&(i.el=H.createElement(De(i.h,i.h[0]),this.options)),i);if(this._$AH?._$AD===a)this._$AH.p(t);else{let s=new W(a,this),n=s.u(this.options);s.p(t),this.T(n),this._$AH=s}}_$AC(e){let t=we.get(e.strings);return t===void 0&&we.set(e.strings,t=new H(e)),t}k(e){J(this._$AH)||(this._$AH=[],this._$AR());let t=this._$AH,i,a=0;for(let s of e)a===t.length?t.push(i=new o(this.O(q()),this.O(q()),this,this.options)):i=t[a],i._$AI(s),a++;a<t.length&&(this._$AR(i&&i._$AB.nextSibling,a),t.length=a)}_$AR(e=this._$AA.nextSibling,t){for(this._$AP?.(!1,!0,t);e!==this._$AB;){let i=_e(e).nextSibling;_e(e).remove(),e=i}}setConnected(e){this._$AM===void 0&&(this._$Cv=e,this._$AP?.(e))}},F=class{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(e,t,i,a,s){this.type=1,this._$AH=g,this._$AN=void 0,this.element=e,this.name=t,this._$AM=a,this.options=s,i.length>2||i[0]!==""||i[1]!==""?(this._$AH=Array(i.length-1).fill(new String),this.strings=i):this._$AH=g}_$AI(e,t=this,i,a){let s=this.strings,n=!1;if(s===void 0)e=S(this,e,t,0),n=!O(e)||e!==this._$AH&&e!==k,n&&(this._$AH=e);else{let r=e,l,p;for(e=s[0],l=0;l<s.length-1;l++)p=S(this,r[i+l],t,l),p===k&&(p=this._$AH[l]),n||(n=!O(p)||p!==this._$AH[l]),p===g?e=g:e!==g&&(e+=(p??"")+s[l+1]),this._$AH[l]=p}n&&!a&&this.j(e)}j(e){e===g?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,e??"")}},Y=class extends F{constructor(){super(...arguments),this.type=3}j(e){this.element[this.name]=e===g?void 0:e}},G=class extends F{constructor(){super(...arguments),this.type=4}j(e){this.element.toggleAttribute(this.name,!!e&&e!==g)}},X=class extends F{constructor(e,t,i,a,s){super(e,t,i,a,s),this.type=5}_$AI(e,t=this){if((e=S(this,e,t,0)??g)===k)return;let i=this._$AH,a=e===g&&i!==g||e.capture!==i.capture||e.once!==i.once||e.passive!==i.passive,s=e!==g&&(i===g||a);a&&this.element.removeEventListener(this.name,this,i),s&&this.element.addEventListener(this.name,this,e),this._$AH=e}handleEvent(e){typeof this._$AH=="function"?this._$AH.call(this.options?.host??this.element,e):this._$AH.handleEvent(e)}},Z=class{constructor(e,t,i){this.element=e,this.type=6,this._$AN=void 0,this._$AM=t,this.options=i}get _$AU(){return this._$AM._$AU}_$AI(e){S(this,e)}};var Ye=T.litHtmlPolyfillSupport;Ye?.(H,U),(T.litHtmlVersions??(T.litHtmlVersions=[])).push("3.3.2");var ke={ATTRIBUTE:1,CHILD:2,PROPERTY:3,BOOLEAN_ATTRIBUTE:4,EVENT:5,ELEMENT:6},Ce=o=>(...e)=>({_$litDirective$:o,values:e}),z=class{constructor(e){}get _$AU(){return this._$AM._$AU}_$AT(e,t,i){this._$Ct=e,this._$AM=t,this._$Ci=i}_$AS(e,t){return this.update(e,t)}update(e,t){return this.render(...t)}};var j=class extends z{constructor(e){if(super(e),this.it=g,e.type!==ke.CHILD)throw Error(this.constructor.directiveName+"() can only be used in child bindings")}render(e){if(e===g||e==null)return this._t=void 0,this.it=e;if(e===k)return e;if(typeof e!="string")throw Error(this.constructor.directiveName+"() called with a non-string value");if(e===this.it)return this._t;this.it=e;let t=[e];return t.raw=t,this._t={_$litType$:this.constructor.resultType,strings:t,values:[]}}};j.directiveName="unsafeHTML",j.resultType=1;var Se=Ce(j);var Fe=Object.getPrototypeOf(customElements.get("ha-panel-lovelace")),c=Fe.prototype.html,Ge=Fe.prototype.css;Date.prototype.getWeekNumber=function(){var o=new Date(+this);return o.setHours(0,0,0,0),o.setDate(o.getDate()+4-(o.getDay()||7)),Math.ceil(((o-new Date(o.getFullYear(),0,1))/864e5+1)/7)};var Xe=["mp3","m4a","aac","wav","ogg","oga","opus","flac"],Ze=["mp4","webm","mov","m4v"],ee=class extends _{constructor(){super(...arguments);this.lunchBreakRendered=!1}initCard(){}getFormattedDate(t){return new Date(t).toLocaleDateString("fr-FR",{weekday:"long",day:"2-digit",month:"2-digit"}).replace(/^(.)/,i=>i.toUpperCase())}getDayHeader(t,i){return c`<div class="ed-devoir-header">
      ${this.config.enable_slider?c`<span
            class="ed-devoir-header-arrow-left ${i===0?"disabled":""}"
            @click=${a=>this.changeDay("previous",a)}
            >←</span
          >`:""}
      <span class="ed-devoir-header-date"
        >${this.getFormattedDate(t.date)}</span
      >
      ${this.config.enable_slider?c`<span
            class="ed-devoir-header-arrow-right"
            @click=${a=>this.changeDay("next",a)}
            >→</span
          >`:""}
    </div>`}changeDay(t,i){if(i.preventDefault(),i.target.classList.contains("disabled"))return;let a=i.target.parentElement.parentElement,s=a.previousElementSibling&&a.previousElementSibling.classList.contains("ed-devoir-day-wrapper"),n=a.nextElementSibling&&a.nextElementSibling.classList.contains("ed-devoir-day-wrapper"),r=null;t==="previous"&&s?r=a.previousElementSibling:t==="next"&&n&&(r=a.nextElementSibling),r&&(a.classList.remove("active"),r.classList.add("active"),s=r.previousElementSibling&&r.previousElementSibling.classList.contains("ed-devoir-day-wrapper"),n=r.nextElementSibling&&r.nextElementSibling.classList.contains("ed-devoir-day-wrapper"),s||r.querySelector(".ed-devoir-header-arrow-left").classList.add("disabled"),n||r.querySelector(".ed-devoir-header-arrow-right").classList.add("disabled"))}getMediaKind(t){let i=String(t||"").split(".").pop().toLowerCase();return Xe.includes(i)?"audio":Ze.includes(i)?"video":"file"}async getDocumentUrl(t,i){let a=await this.hass.callWS({type:"auth/sign_path",path:`/api/ecole_directe/document/${encodeURIComponent(t.id)}${i?"?download=1":""}`,expires:3600});return this.hass.hassUrl(a.path)}setDocumentState(t,i){this._documentStates={...this._documentStates||{},[t.id]:i},this.requestUpdate()}async downloadDocument(t,i){i.preventDefault(),i.stopPropagation(),this.setDocumentState(t,"loading");try{let a=window.document.createElement("a");a.href=await this.getDocumentUrl(t,!0),a.download=t.libelle||"",a.rel="noopener",window.document.body.appendChild(a),a.click(),a.remove(),this.setDocumentState(t,null)}catch(a){console.error("Error downloading document",t.id,a),this.setDocumentState(t,"error")}}async playDocument(t,i,a){a.preventDefault(),a.stopPropagation();let s=this._player&&this._player.id===t.id;if(this.closePlayer(),!s){this.setDocumentState(t,"loading");try{let n=await this.getDocumentUrl(t,!1);this._player={id:t.id,kind:i,url:n},this.setDocumentState(t,null)}catch(n){console.error("Error opening document",t.id,n),this.setDocumentState(t,"error")}}}closePlayer(t=null){t&&(t.preventDefault(),t.stopPropagation());let i=this.shadowRoot?.querySelector(".devoir-document-player audio, .devoir-document-player video");i&&(i.pause(),i.removeAttribute("src"),i.load()),this._player&&(this._player=null,this.requestUpdate())}disconnectedCallback(){this.closePlayer(),super.disconnectedCallback()}getDocumentRow(t){let i=this.getMediaKind(t.libelle),a=this._documentStates?.[t.id],s=this._player&&this._player.id===t.id?this._player:null;return c`
      <div class="devoir-document">
        <span
          class="devoir-document-link"
          title="${i==="file"?"T\xE9l\xE9charger":"Lire"}"
          @click=${r=>i==="file"?this.downloadDocument(t,r):this.playDocument(t,i,r)}
        >
          <ha-icon icon="${i==="audio"?"mdi:file-music-outline":i==="video"?"mdi:file-video-outline":"mdi:file-document-outline"}"></ha-icon>
          <span>${t.libelle}</span>
        </span>
        ${i!=="file"?c`<ha-icon
              class="devoir-document-action"
              icon="mdi:download"
              title="Télécharger"
              @click=${r=>this.downloadDocument(t,r)}
            ></ha-icon>`:c``}
        ${a==="loading"?c`<span class="devoir-document-status">Chargement…</span>`:a==="error"?c`<span class="devoir-document-status error">Erreur</span>`:c``}
      </div>
      ${s?c`<div class="devoir-document-player">
            ${s.kind==="audio"?c`<audio controls autoplay src="${s.url}"></audio>`:c`<video
                  controls
                  autoplay
                  playsinline
                  src="${s.url}"
                ></video>`}
            <ha-icon
              class="devoir-document-action"
              icon="mdi:close"
              title="Fermer"
              @click=${r=>this.closePlayer(r)}
            ></ha-icon>
          </div>`:c``}
    `}getdevoirRow(t,i){if(!t)return c``;let a=t.description||t.short_description||"",s=(typeof a=="string"?a:String(a)).trim().replace(/\n/g,"<br />");return c`
      <tr class="${t.effectue?"devoir-done":""}">
        <td class="devoir-detail">
          <label for="devoir-${i}">
            <span class="devoir-subject">${t.matiere||""}</span>
            ${t.interrogation?c`<span class="devoir-controle">(Contrôle)</span>`:c``}
          </label>
          <input type="checkbox" id="devoir-${i}" />
          <span class="devoir-description">${Se(s)}</span>
          ${Array.isArray(t.documents)&&t.documents.length>0?c`
                <div class="devoir-documents">
                  <ha-icon icon="mdi:file-document-multiple-outline"></ha-icon>
                  <span>
                    ${t.documents.length} document${t.documents.length>1?"s":""}
                  </span>
                </div>

                <div class="devoir-document-list">
                  ${t.documents.map(n=>this.getDocumentRow(n))}
                </div>
              `:c``}
        </td>
        <td class="devoir-status">
          <span
            >${t.effectue?c`<ha-icon icon="mdi:check"></ha-icon>`:c`<ha-icon icon="mdi:account-clock"></ha-icon>`}</span
          >
        </td>
      </tr>
    `}getDayRow(t,i,a){return c`
      <div
        class="${this.config.enable_slider?"slider-enabled":""} ed-devoir-day-wrapper ${a===0?"active":""}"
      >
        ${this.getDayHeader(t,a)}
        <table class="${this.config.reduce_done_devoir?"reduce-done":""}">
          ${i}
        </table>
      </div>
    `}render(){if(!this.config||!this.hass)return c`<div class="ed-card-no-data">
        Veuillez configurer la carte
      </div>`;let t=this.hass.states[this.config.entity];if(t){let i=t.attributes.Devoirs;if(i){if(i.length>0&&i[0].stored_in_store){let r=i[0].store_key;if(this._storedData&&this._storedData[r])i=this._storedData[r];else return this._fetchingKeys||(this._fetchingKeys={}),this._fetchingKeys[r]||(this._fetchingKeys[r]=!0,this.hass.callWS({type:"ecole_directe/get_stored_data",key:r}).then(l=>{this._storedData||(this._storedData={}),this._storedData[r]=l.data||[],this.requestUpdate()}).catch(l=>{console.error("Error fetching stored data for key",r,l)})),c`<div class="ed-card-no-data">Chargement des devoirs...</div>`}let a=[],s=[],n=0;if(i&&i.length>0){if(i[0].Erreur)return c`<div class="ed-card-no-data">${i[0].Erreur}</div>`;let r=this.getFormattedDate(i[0].date);for(let l=0;l<i.length;l++){let p=i[l],u=this.getFormattedDate(p.date);p.effectue===!0&&this.config.display_done_devoir===!1||(r!==u&&(s.length>0&&(a.push(this.getDayRow(i[l-1],s,n)),s=[]),r=u,n++),s.push(this.getdevoirRow(p,l)))}s.length>0&&a.push(this.getDayRow(i[i.length-1],s,n))}return a.length===0&&a.push(this.noDataMessage()),c` <ha-card
          id="${this.config.entity}-card"
          class="${this.config.enable_slider?"ed-devoir-card-slider":""}"
        >
          ${this.config.display_header?this.getCardHeader():""}
          ${a}
        </ha-card>`}}return c`<div class="ed-card-no-data">
      Veuillez choisir une autre entité
    </div>`}setConfig(t){if(!t.entity)throw new Error("Vous devez d\xE9finir une entit\xE9");let i={entity:null,display_header:!0,reduce_done_devoir:!0,display_done_devoir:!0,enable_slider:!1};this.config={...i,...t},this.header_title="Devoirs de ",this.no_data_message="Pas de devoirs \xE0 faire"}static get styles(){return Ge`
      ${super.styles}
      .ed-devoir-card-slider .ed-devoir-day-wrapper {
        display: none;
      }
      .ed-devoir-card-slider .ed-devoir-day-wrapper.active {
        display: block;
      }
      .ed-devoir-card-slider .ed-devoir-header-date {
        display: inline-block;
        text-align: center;
        width: 120px;
      }
      .ed-devoir-header-arrow-left,
      .ed-devoir-header-arrow-right {
        cursor: pointer;
      }
      .ed-devoir-header-arrow-left.disabled,
      .ed-devoir-header-arrow-right.disabled {
        opacity: 0.3;
        pointer-events: none;
      }
      div:not(.slider-enabled) > .ed-devoir-header {
        border-bottom: 2px solid grey;
      }
      .slider-enabled > .ed-devoir-header {
        padding-top: 0;
        text-align: center;
      }
      table {
        font-size: 0.9em;
        font-family: Roboto;
        width: 100%;
        outline: 0px solid #393c3d;
        border-collapse: collapse;
      }
      td {
        vertical-align: top;
        padding: 5px 10px 5px 10px;
        padding-top: 8px;
        text-align: left;
      }
      td.devoir-detail {
        padding: 0;
        padding-top: 8px;
        padding-bottom: 8px;
      }
      span.devoir-subject {
        display: block;
        font-weight: bold;
      }
      span.devoir-controle {
        display: block;
        font-weight: bold;
        color: red;
      }
      span.devoir-description {
        font-size: 0.9em;
      }
      td.devoir-status {
        width: 5%;
      }
      .reduce-done .devoir-done label:hover {
        cusor: pointer;
      }
      .reduce-done .devoir-done .devoir-description,
      .reduce-done .devoir-done .devoir-documents,
      .reduce-done .devoir-done .devoir-document-list {
        display: none;
      }
      .reduce-done .devoir-done input:checked + .devoir-description {
        display: block;
      }
      .reduce-done .devoir-done input:checked ~ .devoir-documents {
        display: flex;
      }
      .reduce-done .devoir-done input:checked ~ .devoir-document-list {
        display: block;
      }
      .devoir-detail input {
        display: none;
      }
      .devoir-documents {
        display: flex;
        align-items: center;
        gap: 5px;
        margin-top: 3px;
        padding-top: 0px;
        padding-top: 2px;
        padding-bottom: 2px;
        padding-left: 0px;
        font-size: 0.85em;
        opacity: 0.8;
      }
      .devoir-documents ha-icon {
        --mdc-icon-size: 18px;
      }
      .devoir-document-list {
        margin-top: 5px;
        margin-left: 0px;
        padding-top: 0px;
        padding-left: 4px;
      }
      .devoir-document {
        display: flex;
        align-items: flex-start;
        gap: 6px;
        margin: 0px;
        padding: 0px;
        padding-left: 4px;
        font-size: 0.82em;
        opacity: 0.85;
      }
      .devoir-document ha-icon {
        flex-shrink: 0;
        --mdc-icon-size: 16px;
      }
      .devoir-document-link {
        display: flex;
        align-items: flex-start;
        gap: 6px;
        cursor: pointer;
      }
      .devoir-document-link:hover span {
        text-decoration: underline;
      }
      .devoir-document-action {
        cursor: pointer;
      }
      .devoir-document-status {
        font-style: italic;
        opacity: 0.8;
      }
      .devoir-document-status.error {
        color: var(--error-color, red);
      }
      .devoir-document-player {
        display: flex;
        align-items: center;
        gap: 6px;
        padding: 4px 0 4px 4px;
      }
      .devoir-document-player audio,
      .devoir-document-player video {
        flex: 1;
        min-width: 0;
        max-width: 100%;
      }
      .devoir-document-player ha-icon {
        --mdc-icon-size: 18px;
      }
    `}static getStubConfig(){return{display_header:!0,reduce_done_devoir:!0,display_done_devoir:!0,enable_slider:!1}}static getConfigElement(){return document.createElement("ecole_directe-devoirs-card-editor")}};customElements.define("ecole_directe-devoirs-card",ee);window.customCards=window.customCards||[];window.customCards.push({type:"ecole_directe-devoirs-card",name:"Carte des devoirs pour Ecole Directe",description:"Affiche les devoirs pour Ecole Directe",documentationURL:"https://github.com/hacf-fr/EcoleDirecteHACards?tab=readme-ov-file#devoirs"});var Re=Object.getPrototypeOf(customElements.get("ha-panel-lovelace")),v=Re.prototype.html,Je=Re.prototype.css,te=class extends _{initCard(){this.items_attribute_key="notes",this.header_title="Notes de ",this.no_data_message="Aucune note disponible"}getFormattedDate(e){return new Date(e).toLocaleDateString("fr-FR",{weekday:"short",day:"2-digit",month:"2-digit"}).replace(/^(.)/,t=>t.toUpperCase())}getGradeRow(e){let t=parseFloat(e.note.replace(",",".")),i=[];if(this.config.compare_with_ratio!==null){let s=parseFloat(this.config.compare_with_ratio),n=t/parseFloat(e.sur.replace(",","."));i.push(n>=s?"above-ratio":"below-ratio")}else if(this.config.compare_with_class_average&&e.moyenne_classe){let s=parseFloat(e.moyenne_classe.replace(",","."));i.push(t>=s?"above-average":"below-average")}let a=e.note_sur;if(this.config.grade_format==="short"&&(a=e.note),this.config.display_new_grade_notice&&e.date_saisie){let s=new Date(e.date_saisie),n=new Date;s.getFullYear()===n.getFullYear()&&s.getMonth()===n.getMonth()&&s.getDate()===n.getDate()&&i.push("new-grade")}return v`
      <tr class="${i.join(" ")}">
        <td class="grade-color"><span></span></td>
        <td class="grade-description">
          <span class="grade-subject">${e.matiere}</span>
          ${this.config.display_comment?v`<span class="grade-comment">${e.commentaire}</span>`:""}
          ${this.config.display_date?v`<span class="grade-date"
                >${this.getFormattedDate(e.date)}</span
              >`:""}
          ${this.config.display_coefficient&&e.coefficient?v`<span class="grade-coefficient"
                >Coef. ${e.coefficient}</span
              >`:""}
        </td>
        <td class="grade-detail">
          ${e.non_significatif?v`<span class="grade-value non-significatif">${a}</span>`:v`<span class="grade-value">${a}</span>`}
          ${this.config.display_class_average&&e.moyenne_classe?v`<span class="grade-class-average"
                >Moy. ${e.moyenne_classe}</span
              >`:""}
          ${this.config.display_class_min&&e.min?v`<span class="grade-class-min">Min. ${e.min}</span>`:""}
          ${this.config.display_class_max&&e.max?v`<span class="grade-class-max">Max. ${e.max}</span>`:""}
        </td>
      </tr>
    `}getCardContent(){if(this.hass.states[this.config.entity]){let t=this.getItems(),i=this.config.max_grades??t.length,a=[],s=[];for(let n=0;n<i&&!(n>=t.length);n++){let r=t[n];a.push(this.getGradeRow(r))}return a.length>0?s.push(v`<table>
            ${a}
          </table>`):s.push(this.noDataMessage()),s}}getDefaultConfig(){return{grade_format:"full",display_header:!0,display_date:!0,display_comment:!0,display_class_average:!0,compare_with_class_average:!0,compare_with_ratio:null,display_coefficient:!0,display_class_min:!0,display_class_max:!0,display_new_grade_notice:!0,max_grades:null}}static get styles(){return Je`
      ${super.styles}
      table {
        font-size: 0.9em;
        font-family: Roboto;
        width: 100%;
        outline: 0px solid #393c3d;
        border-collapse: collapse;
      }
      td {
        vertical-align: top;
        padding: 5px 10px 5px 10px;
        padding-top: 8px;
        text-align: left;
      }
      td.grade-color {
        width: 4px;
        padding-top: 11px;
      }
      td.grade-color > span {
        display: inline-block;
        width: 4px;
        height: 1rem;
        border-radius: 4px;
        background-color: grey;
      }
      .above-average .grade-color > span,
      .above-ratio .grade-color > span {
        background-color: green;
      }
      .below-average .grade-color > span,
      .below-ratio .grade-color > span {
        background-color: orange;
      }
      .grade-description {
        padding-left: 0;
      }
      .grade-subject {
        display: inline-block;
        font-weight: bold;
        position: relative;
      }
      .new-grade .grade-subject:after {
        content: " ";
        display: block;
        width: 6px;
        height: 6px;
        border-radius: 6px;
        background-color: orange;
        position: absolute;
        top: 6px;
        right: -14px;
      }
      .grade-comment {
        display: block;
      }
      .grade-date,
      .grade-coefficient {
        font-size: 0.9em;
        color: gray;
      }
      .grade-date + .grade-coefficient:before {
        content: " - ";
      }
      .grade-detail {
        text-align: right;
        width: 40%;
      }
      .grade-value {
        font-weight: bold;
      }
      .grade-value,
      .grade-class-average {
        display: block;
      }
      .non-significatif {
        font-style: italic;
      }
      .grade-class-average,
      .grade-class-min,
      .grade-class-max {
        font-size: 0.9em;
        color: gray;
      }
      .grade-class-min + .grade-class-max:before {
        content: " - ";
      }
    `}static getStubConfig(){return{grade_format:"full",display_header:!0,display_date:!0,display_comment:!0,display_class_average:!0,compare_with_class_average:!0,compare_with_ratio:null,display_coefficient:!0,display_class_min:!0,display_class_max:!0,display_new_grade_notice:!0,max_grades:null}}static getConfigElement(){return document.createElement("ecole_directe-notes-card-editor")}};customElements.define("ecole_directe-notes-card",te);window.customCards=window.customCards||[];window.customCards.push({type:"ecole_directe-notes-card",name:"Carte des notes pour Ecole Directe",description:"Affiche les notes pour Ecole Directe",documentationURL:"https://github.com/hacf-fr/EcoleDirecteHACards?tab=readme-ov-file#notes"});var Le=Object.getPrototypeOf(customElements.get("ha-panel-lovelace")),w=Le.prototype.html,Qe=Le.prototype.css,ie=class extends _{initCard(){this.items_attribute_key="Disciplines",this.header_title="Moyennes de ",this.no_data_message="Aucune moyenne"}getOverallAverageRow(){let e=`${this.config.entity}`;if(!this.hass.states[e])return w``;let t=this.hass.states[e].state;if(!t)return w``;let i=parseFloat(t.replace(",",".")),a=[];if(this.config.compare_with_ratio!==null){let s=parseFloat(this.config.compare_with_ratio);a.push(i>=s?"above-ratio":"below-ratio")}return w`
      <tr class="${a.join(" ")} overall-average">
        <td class="average-color"><span></span></td>
        <td class="average-description">
          <span class="average-subject">Moyenne générale</span>
        </td>
        <td class="average-detail">
          <span class="average-value"
            ><span>${t.replace(".",",")}</span></span
          >
        </td>
      </tr>
    `}getAverageRow(e){let t=parseFloat(e.moyenne.replace(",",".")),i=[];if(this.config.compare_with_ratio!==null){let a=parseFloat(this.config.compare_with_ratio);i.push(t>=a?"above-ratio":"below-ratio")}else if(this.config.compare_with_class_average&&e.moyenneClasse){let a=parseFloat(e.moyenneClasse.replace(",","."));i.push(t>=a?"above-average":"below-average")}return w`
      <tr class="${i.join(" ")}">
        <td class="average-color">
          <span style="background-color:Grey"></span>
        </td>
        <td class="average-description">
          <span class="average-subject">${e.nom}</span>
        </td>
        <td class="average-detail">
          <span class="average-value">${e.moyenne}</span>
          ${this.config.display_class_average&&e.moyenneClasse?w`<span class="average-class-average"
                >Classe ${e.moyenneClasse}</span
              >`:""}
          ${this.config.display_class_min&&e.moyenneMin?w`<span class="average-class-min"
                >Min. ${e.moyenneMin}</span
              >`:""}
          ${this.config.display_class_max&&e.moyenneMax?w`<span class="average-class-max"
                >Max. ${e.moyenneMax}</span
              >`:""}
        </td>
      </tr>
    `}getCardContent(){if(this.hass.states[this.config.entity]){let t=this.getItems(),i=[],a=[];this.config.display_overall_average&&a.push(this.getOverallAverageRow());for(let s=0;s<t.length;s++){let n=t[s];a.push(this.getAverageRow(n))}return a.length>0?i.push(w`<table>
            ${a}
          </table>`):i.push(this.noDataMessage()),i}return[]}getDefaultConfig(){return{display_header:!0,display_class_average:!0,compare_with_class_average:!0,compare_with_ratio:null,display_class_min:!0,display_class_max:!0,display_overall_average:!0}}static get styles(){return Qe`
      ${super.styles}
      table {
        font-size: 0.9em;
        font-family: Roboto;
        width: 100%;
        outline: 0px solid #393c3d;
        border-collapse: collapse;
      }
      td {
        vertical-align: top;
        padding: 5px 10px 5px 10px;
        padding-top: 8px;
        text-align: left;
      }
      tr.overall-average {
        border-bottom: 1px solid #393c3d;
      }
      tr.overall-average td {
        text-transform: uppercase;
        padding-bottom: 10px;
      }
      tr.overall-average .average-value span {
        padding: 5px;
        border-radius: 5px;
        border: 1px solid var(--primary-text-color);
      }
      tr.overall-average tr td {
        padding-top: 10px;
      }
      td.average-comparison-color,
      td.average-color {
        width: 4px;
        padding-top: 11px;
      }
      td.average-comparison-color > span,
      td.average-color > span {
        display: inline-block;
        width: 4px;
        height: 1rem;
        border-radius: 4px;
        background-color: grey;
      }

      .above-average .average-detail,
      .above-ratio .average-detail,
      .below-average .average-detail,
      .below-ratio .average-detail {
        position: relative;
      }
      .above-average span.average-value,
      .above-ratio span.average-value,
      .below-average span.average-value,
      .below-ratio span.average-value {
        padding-right: 16px;
      }
      .above-average span.average-value:before,
      .above-ratio span.average-value:before,
      .below-average span.average-value:before,
      .below-ratio span.average-value:before {
        content: " ";
        display: block;
        width: 10px;
        height: 10px;
        border-radius: 5px;
        position: absolute;
        right: 10px;
        top: 13px;
      }
      .above-average span.average-value:before,
      .above-ratio span.average-value:before {
        background-color: green;
      }
      .below-average span.average-value:before,
      .below-ratio span.average-value:before {
        background-color: orange;
      }
      .average-description {
        padding-left: 0;
      }
      .average-subject {
        display: inline-block;
        font-weight: bold;
        position: relative;
      }
      .average-detail {
        text-align: right;
      }
      .average-value {
        font-weight: bold;
      }
      .average-value,
      .average-class-average {
        display: block;
      }
      .average-class-average,
      .average-class-min,
      .average-class-max {
        font-size: 0.9em;
        color: gray;
      }
      .average-class-min + .average-class-max:before {
        content: " - ";
      }
    `}static getStubConfig(){return{display_header:!0,display_class_average:!0,compare_with_class_average:!0,compare_with_ratio:null,display_class_min:!0,display_class_max:!0}}static getConfigElement(){return document.createElement("ecole_directe-moyennes-card-editor")}};customElements.define("ecole_directe-moyennes-card",ie);window.customCards=window.customCards||[];window.customCards.push({type:"ecole_directe-moyennes-card",name:"Carte des moyennes pour Ecole Directe",description:"Affiche les moyennes pour Ecole Directe",documentationURL:"https://github.com/hacf-fr/EcoleDirecteHACards?tab=readme-ov-file#moyennes"});var Te=Object.getPrototypeOf(customElements.get("ha-panel-lovelace")),b=Te.prototype.html,et=Te.prototype.css,ae=class extends _{initCard(){this.items_attribute_key="Evaluations",this.header_title="Evaluations de ",this.no_data_message="Pas d'\xE9valuation \xE0 afficher"}getFormattedDate(e){return new Date(e).toLocaleDateString("fr-FR",{weekday:"short",day:"2-digit",month:"2-digit"}).replace(/^(.)/,t=>t.toUpperCase())}getAcquisitionRow(e,t){return b`
      <tr class="acquisition-row acquisition-row-${t}">
        <td></td>
        <td colspan="2">
          <div class="acquisition-item">
            <span class="acquisition-description">
              <span class="acquisition-label">${e.competence}</span>${e.descriptif?b`<span class="acquisition-detail">${e.descriptif}</span>`:""}
            </span>
            ${this.getAcquisitionIcon(e)}
          </div>
        </td>
      </tr>
    `}getAcquisitionIcon(e){let t=this.config.mapping_evaluations[e.valeur]||e.valeur,i="";return t==="A+"?i="+":t==="Abs"&&(i="a"),b`
      <div class="acquisition-status">
        <span
          title="${e.level||""}"
          class="acquisition-icon acquisition-icon-${t}"
        >
          ${i}
        </span>
      </div>
    `}toggleEvaluation(e){let t=e.currentTarget,i=t.closest(".evaluation-group");i&&i.classList.toggle("open",t.checked)}getEvaluationRow(e,t){let i=e.elements_programme,a=[],s=[],n="grey";for(let r=0;r<i.length;r++)a.push(this.getAcquisitionIcon(i[r])),s.push(this.getAcquisitionRow(i[r],t));return b`
      <tbody class="evaluation-group">
        <tr class="evaluation-row">
          <td class="evaluation-color">
            <span style="background-color:${n}"></span>
          </td>
          <td class="evaluation-description">
            <label for="evaluation-full-detail-${t}">
              <span class="evaluation-subject">${e.matiere}</span>
            </label>
            <input type="checkbox" id="evaluation-full-detail-${t}" @change="${this.toggleEvaluation}" />
            ${this.config.display_comment?b`<span class="evaluation-comment">${e.devoir}</span>`:""}
            ${this.config.display_date?b`<span class="evaluation-date"
                  >${this.getFormattedDate(e.date)}</span
                >`:""}
          </td>
          <td class="evaluation-detail">${a}</td>
        </tr>
        ${s}
      </tbody>
    `}getLegendHeader(){let t=this.hass.states[this.config.entity]?.attributes?.level_mapping;return t?b`
      <div class="evaluation-legend">
        <span class="legend-item"><span class="acquisition-icon acquisition-icon-4"></span> ${t[4]}</span>
        <span class="legend-item"><span class="acquisition-icon acquisition-icon-3"></span> ${t[3]}</span>
        <span class="legend-item"><span class="acquisition-icon acquisition-icon-2"></span> ${t[2]}</span>
        <span class="legend-item"><span class="acquisition-icon acquisition-icon-1"></span> ${t[1]}</span>
      </div>
    `:b``}getCardContent(){if(this.hass.states[this.config.entity]){let t=this.getItems(),i=this.config.max_evaluations??t.length,a=[],s=[];s.push(this.getLegendHeader());for(let n=0;n<i&&!(n>=t.length);n++){let r=t[n];a.push(this.getEvaluationRow(r,n))}return a.length>0?s.push(b`<table>
            ${a}
          </table>`):s.push(this.noDataMessage()),s}return[]}getDefaultConfig(){return{display_header:!0,display_description:!0,display_teacher:!0,display_date:!0,display_comment:!0,max_evaluations:null,mapping_evaluations:{}}}static get styles(){return et`
      ${super.styles}
      table {
        font-size: 0.9em;
        font-family: Roboto;
        width: 100%;
        outline: 0px solid #393c3d;
        border-collapse: collapse;
      }
      td {
        vertical-align: top;
        padding: 5px 10px 5px 10px;
        text-align: left;
      }
      td.evaluation-color {
        width: 4px;
        padding-top: 8px;
      }
      td.evaluation-color > span {
        display: inline-block;
        width: 4px;
        height: 4rem;
        border-radius: 4px;
        background-color: grey;
      }
      .above-average .evaluation-color > span,
      .above-ratio .evaluation-color > span {
        background-color: green;
      }
      .below-average .evaluation-color > span,
      .below-ratio .evaluation-color > span {
        background-color: orange;
      }
      .evaluation-subject {
        font-weight: bold;
        display: block;
      }
      .evaluation-description {
        display: block;
        padding-left: 0px;
      }
      .evaluation-teacher {
        display: block;
      }
      .evaluation-date,
      .evaluation-coefficient {
        font-size: 0.9em;
        color: gray;
      }
      .evaluation-comment {
        display: block;
      }
      .evaluation-date + .evaluation-coefficient:before {
        content: " - ";
      }
      .evaluation-detail {
        text-align: right;
      }
      .evaluation-value {
        font-weight: bold;
      }
      .evaluation-legend {
        display: flex;
        flex-wrap: wrap;
        gap: 4px 6px;
        align-items: center;
        padding: 8px 12px;
        margin-bottom: 8px;
        border-bottom: 1px solid var(--divider-color, rgba(0, 0, 0, 0.12));
        font-size: 0.85em;
        font-weight: normal;
        color: var(--secondary-text-color, gray);
      }
      .evaluation-legend div, .legend-item {
        padding: 0;
        font-weight: normal;
        font-size: inherit;
      }
      .legend-item {
        padding-right: 5px;
        display: inline-flex;
        align-items: center;
        gap: 6px; /* espace propre entre la bulle et le texte */
      }
      .acquisition-status {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 5px 0px 0px 0px;
        white-space: nowrap;
      }
      .acquisition-icon {
        display: inline-block;
        width: 14px;
        height: 14px;
        border-radius: 50%;
        border: solid 0.02em rgba(0, 0, 0, 0.5);
        margin-left: 4px;
        vertical-align: middle;
        color: white;
        content: "+";
        text-align: center;
        line-height: 14px;
      }
      .acquisition-icon-4 {
        background-color: rgb(0, 176, 80);
      }
      .acquisition-icon-3 {
        background-color: rgb(0, 112, 192);
      }
      .acquisition-icon-2 {
        background-color: rgb(255, 192, 0);
      }
      .acquisition-icon-1 {
        background-color: #f80a0a;
      }
      input[type="checkbox"] {
        display: none;
      }
      .evaluation-group.open .evaluation-row .evaluation-detail {
        display: none;
      }
      .evaluation-description label {
        cursor:pointer;
      }
      .acquisition-row {
        display:none;
      }
      .evaluation-group.open .acquisition-row {
        display:table-row;
      }
      input[type="checkbox"] {
        display:none;
      }
      .acquisition-row td {
        padding: 0px 10px 5px 0px;
      }
      .acquisition-item {
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        padding: 3px 0;
      }
      .acquisition-description {
        min-width: 0;
        padding-right: 10px;
      }
      .acquisition-label {
        display: block;
        font-weight: 500;
      }
      .acquisition-detail {
        display: block;
        font-size: 0.85em;
        color: gray;
        margin-top: 2px;
      }
      .acquisition-item .acquisition-icon {
        flex-shrink: 0;
        margin-left: 8px;
      }
      .acquisition-row td:nth-child(2) {
        text-align: left;
      }
    `}static getStubConfig(){return{display_header:!0,display_description:!0,display_teacher:!0,display_date:!0,display_comment:!0,max_evaluations:null,mapping_evaluations:{}}}static getConfigElement(){return document.createElement("ecole_directe-evaluations-card-editor")}};customElements.define("ecole_directe-evaluations-card",ae);window.customCards=window.customCards||[];window.customCards.push({type:"ecole_directe-evaluations-card",name:"Carte des \xE9valuations pour Ecole Directe",description:"Affiche les \xE9valuations pour Ecole Directe",documentationURL:"https://github.com/hacf-fr/EcoleDirecteHACards?tab=readme-ov-file#evaluations"});var Oe=Object.getPrototypeOf(customElements.get("ha-panel-lovelace")),M=Oe.prototype.html,tt=Oe.prototype.css,se=class extends _{getAbsencesRetardsRow(e){let t=M`
      <tr>
        <td class="absence-status">
          <span
            >${e.justifie?M`<ha-icon icon="mdi:check"></ha-icon>`:M`<ha-icon icon="mdi:clock-alert-outline"></ha-icon>`}</span
          >
        </td>
        <td>
          <span
            style="background-color:${e.justifie?"#107c41":"#e73a1f"}"
          ></span>
        </td>
        <td>
          <span class="absence-from">${e.display_date}</span
          ><br /><span class="absence-hours">${e.libelle}</span>
        </td>
        <td>
          <span class="absence-reason">${e.motif}</span>
        </td>
      </tr>
    `;return M`${t}`}initCard(){this.hass.states[this.config.entity].attributes.Absences?(this.items_attribute_key="Absences",this.header_title="Absences de ",this.no_data_message="Aucune absence"):(this.items_attribute_key="Retards",this.header_title="Retards de ",this.no_data_message="Aucun retard")}getCardContent(){if(this.hass.states[this.config.entity]){let t=this.getItems(),i=[],a=[];for(let s=0;s<t.length&&!(this.config.max&&this.config.max<s);s++)a.push(this.getAbsencesRetardsRow(t[s]));return t.length>0?i.push(M`<table>
            ${a}
          </table>`):i.push(this.noDataMessage()),i}}getDefaultConfig(){return{display_header:!0,max:null}}static get styles(){return tt`
      ${super.styles}
      table {
        clear: both;
        font-size: 0.9em;
        font-family: Roboto;
        width: 100%;
        outline: 0px solid #393c3d;
        border-collapse: collapse;
      }
      tr:nth-child(odd) {
        background-color: rgba(0, 0, 0, 0.1);
      }
      td {
        vertical-align: middle;
        padding: 5px 10px 5px 10px;
        text-align: left;
      }
      tr td:first-child {
        width: 10%;
        text-align: right;
      }
      span.absence-reason {
        font-weight: bold;
        display: block;
      }
      tr td:nth-child(2) {
        width: 4px;
        padding: 5px 0;
      }
      tr td:nth-child(2) > span {
        display: inline-block;
        width: 4px;
        height: 3rem;
        border-radius: 4px;
        background-color: grey;
        margin-top: 4px;
      }
      span.absence-from {
        font-weight: bold;
        padding: 4px;
        border-radius: 4px;
      }
      span.absence-hours {
        font-size: 0.9em;
        padding: 4px;
      }
      table + div {
        border-top: 1px solid white;
      }
    `}static getStubConfig(){return{display_header:!0,max:null}}static getConfigElement(){return document.createElement("ecole_directe-absences-retards-card-editor")}};customElements.define("ecole_directe-absences-retards-card",se);window.customCards=window.customCards||[];window.customCards.push({type:"ecole_directe-absences-retards-card",name:"Carte Absences/Retards pour Ecole Directe",description:"Affiche les absences ou les retards pour Ecole Directe",documentationURL:"https://github.com/hacf-fr/EcoleDirecteHACards?tab=readme-ov-file#absences"});var oe=Object.getPrototypeOf(customElements.get("ha-panel-lovelace")),R=oe.prototype.html,it=oe.prototype.css,ne=class extends oe{static get properties(){return{hass:{},_config:{}}}setConfig(e){this._config=e,this.loadEntityPicker()}_valueChanged(e){let t=Object.assign({},this._config);typeof e.target.checked<"u"?t[e.target.configValue]=e.target.checked:t[e.target.configValue]=e.target.value==""?null:e.target.value,this._config=t;let i=new CustomEvent("config-changed",{detail:{config:t},bubbles:!0,composed:!0});this.dispatchEvent(i)}buildSelectField(e,t,i,a,s){let n=[];for(let r=0;r<i.length;r++){let l=i[r];n.push(R`<ha-list-item .value="${l.value}"
          >${l.label}</ha-list-item
        >`)}return R`
      <ha-select
        label="${e}"
        .value=${a||s}
        .configValue=${t}
        @change=${this._valueChanged}
        @closed=${r=>r.stopPropagation()}
      >
        ${n}
      </ha-select>
    `}buildSwitchField(e,t,i,a){return typeof i!="boolean"&&(i=a),R`
      <ha-formfield class="switch-wrapper" .label="${e}">
        <ha-switch
          name="${t}"
          .checked=${i}
          .configValue="${t}"
          @change=${this._valueChanged}
        ></ha-switch>
      </ha-formfield>
    `}buildNumberField(e,t,i,a,s){return R`
      <ha-textfield
        type="number"
        step="${s||1}"
        label="${e}"
        .value=${i||a}
        .configValue=${t}
        @change=${this._valueChanged}
      >
      </ha-textfield>
    `}buildTextField(e,t,i,a){return R`
      <ha-textfield
        label="${e}"
        .value=${i||a}
        .configValue=${t}
        @change=${this._valueChanged}
        @keyup=${this._valueChanged}
      >
      </ha-textfield>
    `}buildEntityPickerField(e,t,i,a){let s=new RegExp("ed_(.*)_"+a);return R`
      <ha-entity-picker
        label="${e}"
        .hass=${this.hass}
        .value=${i||""}
        .configValue=${t}
        .includeDomains="sensor"
        .entityFilter="${n=>s.test(n.entity_id)}"
        @value-changed=${this._valueChanged}
        allow-custom-entity
      ></ha-entity-picker>
    `}async loadEntityPicker(){if(window.customElements.get("ha-entity-picker"))return;await(await(await window.loadCardHelpers()).createCardElement({type:"entities",entities:[]})).constructor.getConfigElement()}static get styles(){return it`
      ha-formfield {
        display: block;
        padding-top: 20px;
        clear: right;
      }
      ha-formfield > ha-switch {
        float: right;
      }
      ha-select,
      ha-textfield {
        clear: right;
        width: 100%;
        padding-top: 15px;
      }
    `}},f=ne;var at=Object.getPrototypeOf(customElements.get("ha-panel-lovelace")),He=at.prototype.html,re=class extends f{render(){return!this.hass||!this._config?He``:He`
      ${this.buildEntityPickerField("Timetable entity","entity",this._config.entity,"emploi_du_temps_(semaine_en_cours|semaine_suivante|semaine_apres_suivante|aujourd_hui|demain|jour_suivant)")}
      ${this.buildSwitchField("Display header","display_header",this._config.display_header,!0)}
      ${this.buildSwitchField("Display classroom","display_classroom",this._config.display_classroom,!0)}
      ${this.buildSwitchField("Display teacher","display_teacher",this._config.display_teacher,!0)}
      ${this.buildSwitchField("Display day hours","display_day_hours",this._config.display_day_hours,!0)}
      ${this.buildSwitchField("Display lunch break","display_lunch_break",this._config.display_lunch_break,!0)}
      ${this.buildSwitchField("Dim ended lessons","dim_ended_lessons",this._config.dim_ended_lessons,!0)}
      ${this.buildSwitchField("Enable slider","enable_slider",this._config.enable_slider,!1)}
      ${this.buildSwitchField("Auto switch to next day (if slider enabled)","switch_to_next_day",this._config.switch_to_next_day,!1)}
      ${this.buildSwitchField("Display free time slots","display_free_time_slots",this._config.display_free_time_slots,!0)}
    `}};customElements.define("ecole_directe-emploi_temps-card-editor",re);var st=Object.getPrototypeOf(customElements.get("ha-panel-lovelace")),je=st.prototype.html,le=class extends f{render(){return!this.hass||!this._config?je``:je`
      ${this.buildEntityPickerField("Devoir entity","entity",this._config.entity,"devoirs($|_(semaine_en_cours|semaine_suivante|semaine_apres_suivante|aujourd_hui|demain|jour_suivant))")}
      ${this.buildSwitchField("Display header","display_header",this._config.display_header)}
      ${this.buildSwitchField("Reduce done devoir","reduce_done_devoir",this._config.reduce_done_devoir)}
      ${this.buildSwitchField("Display done devoir","display_done_devoir",this._config.display_done_devoir)}
      ${this.buildSwitchField("Enable slider","enable_slider",this._config.enable_slider,!1)}
    `}};customElements.define("ecole_directe-devoirs-card-editor",le);var nt=Object.getPrototypeOf(customElements.get("ha-panel-lovelace")),Me=nt.prototype.html,de=class extends f{render(){return!this.hass||!this._config?Me``:Me`
      ${this.buildEntityPickerField("Notes entity","entity",this._config.entity,"notes")}
      ${this.buildSwitchField("Display header","display_header",this._config.display_header)}
      ${this.buildSwitchField("Display date","display_date",this._config.display_date)}
      ${this.buildSwitchField("Display comment","display_comment",this._config.display_comment)}
      ${this.buildSwitchField("Display class average","display_class_average",this._config.display_class_average)}
      ${this.buildSwitchField("Compare with class average","compare_with_class_average",this._config.compare_with_class_average)}
      ${this.buildSelectField("Grade format","grade_format",[{value:"full",label:"Full"},{value:"short",label:"Short"}],this._config.grade_format)}
      ${this.buildSwitchField("Display coefficient","display_coefficient",this._config.display_coefficient)}
      ${this.buildSwitchField("Display class min","display_class_min",this._config.display_class_min)}
      ${this.buildSwitchField("Display class max","display_class_max",this._config.display_class_max)}
      ${this.buildSwitchField("Display new grade notice","display_new_grade_notice",this._config.display_new_grade_notice)}
    `}};customElements.define("ecole_directe-notes-card-editor",de);var ot=Object.getPrototypeOf(customElements.get("ha-panel-lovelace")),Pe=ot.prototype.html,ce=class extends f{render(){return!this.hass||!this._config?Pe``:Pe`
      ${this.buildEntityPickerField("Evaluations entity","entity",this._config.entity,"evaluations")}
      ${this.buildSwitchField("Display header","display_header",this._config.display_header)}
      ${this.buildSwitchField("Display description","display_description",this._config.display_description)}
      ${this.buildSwitchField("Display teacher","display_teacher",this._config.display_teacher)}
      ${this.buildSwitchField("Display date","display_date",this._config.display_date)}
      ${this.buildSwitchField("Display comment","display_comment",this._config.display_comment)}
      ${this.buildNumberField("Max evaluations","max_evaluations",this._config.max_evaluations)}
    `}};customElements.define("ecole_directe-evaluations-card-editor",ce);var rt=Object.getPrototypeOf(customElements.get("ha-panel-lovelace")),Ne=rt.prototype.html,pe=class extends f{render(){return!this.hass||!this._config?Ne``:Ne`
      ${this.buildEntityPickerField("Cpateur moyennes","entity",this._config.entity,"moyenne_generale")}
      ${this.buildSwitchField("Display header","display_header",this._config.display_header)}
      ${this.buildSwitchField("Display class average","display_class_average",this._config.display_class_average)}
      ${this.buildSwitchField("Compare with class average","compare_with_class_average",this._config.compare_with_class_average)}
      ${this.buildTextField("Compare with ratio","compare_with_ratio",this._config.compare_with_ratio,"")}
      ${this.buildSwitchField("Display class min","display_class_min",this._config.display_class_min)}
      ${this.buildSwitchField("Display class max","display_class_max",this._config.display_class_max)}
      ${this.buildSwitchField("Display overall average","display_overall_average",this._config.display_overall_average,!0)}
    `}};customElements.define("ecole_directe-moyennes-card-editor",pe);var lt=Object.getPrototypeOf(customElements.get("ha-panel-lovelace")),qe=lt.prototype.html,he=class extends f{render(){return!this.hass||!this._config?qe``:qe`
      ${this.buildEntityPickerField("Absences/Retards entity","entity",this._config.entity,"(absences|retards)")}
      ${this.buildSwitchField("Display header","display_header",this._config.display_header)}
      ${this.buildNumberField("Max","max",this._config.max)}
    `}};customElements.define("ecole_directe-absences-retards-card-editor",he);
/*! Bundled license information:

lit-html/lit-html.js:
lit-html/directive.js:
lit-html/directives/unsafe-html.js:
  (**
   * @license
   * Copyright 2017 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)
*/
