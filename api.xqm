(:~
 : This module contains some basic examples for RESTXQ annotations.
 : @author BaseX Team
 :)

module namespace page = 'http://basex.org/examples/web-page';
declare default element namespace 'http://www.oficinaRGB.pt/MakeReservation';
declare namespace r='http://www.oficinaRGB.pt/Reservations';
declare namespace o='http://www.oficinaRGB.pt/Office';
declare namespace f='http://www.oficinaRGB.pt/Family';

(:~
 : Generates a welcome page.
 : @return HTML page
 :)
declare
  %rest:GET
  %rest:path('')
  %output:method('xhtml')
  %output:omit-xml-declaration('no')
  %output:doctype-public('-//W3C//DTD XHTML 1.0 Transitional//EN')
  %output:doctype-system('http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd')
function page:start(
) as element(Q{http://www.w3.org/1999/xhtml}html) {
  <html xmlns='http://www.w3.org/1999/xhtml'>
    <head>
      <title>Welcome to [RGB API]</title>
      <link rel='stylesheet' type='text/css' href='static/style.css'/>
    </head>
    <body>
      <div class='right'><a href='/'><img src='static/basex.svg'/></a></div>
      <h1>How to use this API</h1>
      <div>Welcome to the RGB API. They allow you to:</div>
      <ul>
        <li>create web applications and services with
          <a href='https://docs.basex.org/wiki/RESTXQ'>RESTXQ</a>,</li>
        <li>use full-duplex communication with
          <a href='https://docs.basex.org/wiki/WebSockets'>WebSockets</a>,</li>
        <li>query and modify databases via <a href='https://docs.basex.org/wiki/REST'>REST</a>
          (try <a href='rest'>here</a>), and</li>
        <li>browse and update resources via
          <a href='https://docs.basex.org/wiki/WebDAV'>WebDAV</a>.</li>
      </ul>

      <p>Find more information on the
        <a href='https://docs.basex.org/wiki/Web_Application'>Web Application</a>
        page in our documentation.</p>

      <p>The following sample applications give you a glimpse of how applications
        can be written with BaseX:</p>

      <h3><a href='dba'>DBA: Database Administration</a></h3>

      <p>The Database Administration interface is completely
        written in RESTXQ.<br/>
        The source code helps to understand how complex
        web applications can be built with XQuery.
      </p>

      <h3><a href='chat'>WebSocket Chat</a></h3>

      <p>The chat application demonstrates how bidirectional communication
        is realized with BaseX.<br/>
        For a better experience when testing the chat,
        consider the following steps:
      </p>
        
      <ol>
        <li> Create different database users first (e.g. via the DBA).</li>
        <li> Open two different browsers and log in with different users.</li>
      </ol>
    </body>
  </html>
};



declare %updating
  %rest:path("/makereservation")
  %rest:POST("{$xml}")
  %rest:consumes('application/xml')
  %rest:produces('application/xml')
function page:check-xml($xml)
{
  let $xsd:= "XSD/ReservationPOST.xsd"
  return validate:xsd($xml, $xsd),
  page:storeindb($xml)
};

declare %updating function page:storeindb($xml)
{
  db:add("PEITP", page:queries($xml), concat("reservation", count(db:open("PEITP")//reservation) + 1))
};

declare function page:queries($xml)
{
  let $db := db:open("PEITP")

  (: pfd - prefered Family Dates
     $od - office days 
     $dates the AVAILABLE DATES (result of the comparation)     
  :)
     
  let $pfd := $xml//f:preferedDates/text()
  let $od := $db//o:date/text()
  
  where some $pfd in $od satisfies $pfd=$od
  
  let $date := $db//o:office[o:date = $pfd and o:slots/o:availableSlots > 0][1]/o:date/text()
  let $rid := count($db//r:reservation/@reservationID) + 1
  
  return
  <reservation reservationID="{$rid}">
    <date>{$date}</date>
    <state>Active</state>
    <family>
      {$xml//f:numberElements}
      {$xml//f:familyElement}
      {$xml//f:country}
    </family>
  </reservation>
};


(: ================ Check Availability ================ :)
declare
  %rest:path("/availability")
  %rest:POST("{$date}")
  %rest:consumes('application/xml')
  %rest:produces('application/xml')
function page:check-availability($date)
{
  let $x := db:open("PEITP")

  let $pd := $date/*/*/text()
  let $od := $x//o:date/text()
  
  where some $pd in $od satisfies $pd=$od
  
  for $result in $x//o:office[o:date = $pd]
  let $date := $result//o:date/text()
  let $aS := $result//o:availableSlots/text()
  return concat($aS, " available slots for the date ", $date)
};

  

