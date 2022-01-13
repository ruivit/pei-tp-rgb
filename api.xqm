(: ============= Namespace Declarations ============= :)

module namespace page = 'http://basex.org/examples/web-page';
declare default element namespace 'http://www.atelierRGB.pt/Reservation';
declare namespace a='http://www.atelierRGB.pt/Atelier';
declare namespace f='http://www.atelierRGB.pt/Family'; 

(: ============= Webpage ============= :)

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
      <h1>[RGB API]</h1>
    </body>
  </html>
};


(: ============= POST XML ============= :)

declare %updating
  %rest:path("/makereservation")
  %rest:POST("{$xml}")
  %rest:consumes('application/xml')
  %rest:produces('application/xml')
function page:post-xml($xml)
{
  (: Check XML vs XSD :)
  let $xsd:= "XSD/Reservation.xsd"
  return validate:xsd($xml, $xsd),

  (: Make all the necessary checks
  if all checks are passed, write to DB :)
  page:checks($xml, 1)
};

(: ============= Checks ============= :)

declare %updating function page:checks($xml, $count)
{
  let $database := db:open("RGBDB")
  let $pfd := $xml//f:preferedDates
  let $officedates := $database//a:reservations
  
  (: Check IF the dates that the family choose are in the Workshop Days 
  IF NOT - a new data will be created :)
  let $existingDates := $officedates[a:date = $pfd]
  
  (: Check the dates that the family choose that ARE NOT the in the Workshop 
  IF this variable AND the existingDates are EMPTY then this means that ALL dates are full :)
  let $notExistingDatesAtelier := $pfd[not(.=($officedates//a:date))]
  let $newDate := $notExistingDatesAtelier[1]
  
  (: From the existingDates in the Workshop, filter the ones that have available slots :)
  let $validSlots := $existingDates[a:slots > 0]
  let $validDate := $validSlots[1]/a:date
  
  (: set the reservationID to +1 since this might be a reservation :)
  let $rid := count($database//reservation/@reservationID) + 1
  
  return
  if ( empty($validDate) )
  then ( if (empty($newDate))
         then ( web:error(500, "[ERRO] O atelier do Pai Natal atingiu o máximo de para o(s) dia(s) escolhidos não têm disponibilidade [ERRO]") )
         else ( 
update:output(page:check-between-dates($newDate)),
db:replace("RGBDB", "atelier1.xml", page:new-date($newDate)),
db:add("RGBDB", page:return-xml-reservation($xml, $newDate), concat("reservation", count(db:open("RGBDB")//reservation) + 1, ".xml")),

(:========FeedBack Message========:)
update:output(page:ok($newDate, $rid))
              )
       )
   else ( 
update:output(page:check-between-dates($validDate)),
replace value of node $database//a:reservations[a:date = $validDate]/a:slots with $database//a:reservations[a:date = $validDate]/a:slots - 1,
db:add("RGBDB", page:return-xml-reservation($xml, $validDate), concat("reservation", count(db:open("RGBDB")//reservation) + 1, ".xml")),

(:========FeedBack Message========:)
update:output(page:ok($validDate, $rid))
      )
};


(:==Check if newValidDate is between the allowed dates "16-09-2022 and 25-12-2022"==:)
declare function page:check-between-dates($dateToCheck)
{
  let $firstdate := xs:date("2022-09-15")
  let $lastdate := xs:date("2022-12-26")
  
  return if($dateToCheck>$firstdate and $dateToCheck<$lastdate)
         then()
         else(web:error(500, "[ERROR] As data permitidas são de 16-09-2022 até 25-12-2022 [ERROR]"))
};

(: return a valid xml with the new date to add to the office file:)
declare function page:new-date($newDate)
{
  let $db := db:open("RGBDB")//a:office
  
  return 
  <office xmlns="http://www.atelierRGB.pt/Atelier" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.atelierRGB.pt/Atelier../XSD/Atelier.xsd">
  {$db//a:reservations}
 <reservations xmlns="http://www.atelierRGB.pt/Atelier" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
        <date>{$newDate/text()}</date>
        <slots>49</slots>
  </reservations>
</office>
};

(: return a valid xml with the valid date, that will be used to make a reservation :)
declare function page:return-xml-reservation($xml, $validDate)
{
  let $db := db:open("RGBDB")
  let $rid := count($db//reservation/@reservationID) + 1
    
  return
  <reservation reservationID="{$rid}">
    <id>{$rid}</id>
    <date>{$validDate/text()}</date>
    <state>Active</state>
    <family>
      <numberElements>{count($xml//f:familyElement)}</numberElements>
      {$xml//f:familyElement/*}
      {$xml//f:origin/*}
    </family>
  </reservation>
};



(: ================ Check Availability ================ :)
declare
  %rest:path("/availability")
  %rest:GET
  %rest:query-param("date", "{$getdate}")
function page:check-availability($getdate)
{
  if ($getdate = "all")
  then (
  let $database := db:open("RGBDB")
  let $officedates := $database//a:reservations
  
  let $zeroSlots := $officedates[a:slots = 0]
  
  
  for $x in $zeroSlots
  return concat("Entre o dia 2022-09-16 e 2022-12-25 os dias não existe disponibilidade para o seguinte dia: ", data($x/a:date)))
  else 
      (
    let $db := db:open("RGBDB")//a:office
    for $days in $getdate
    
    let $check := $days = $db//a:date/text()
    let $slots := $db//a:reservations[a:date = $days]/a:slots/text()
    
    (: Check if the given date is between the allowed days :)
    let $checkDates := page:check-between-dates($days)
    
    return if ($check)
    then "Existe disponibilidade para " || $slots || " familias para o dia " || $days
    else "Existe disponibilidade para 50 familias no dia " || $days
      )
  
  (: GET REQUESTs Examples :)
  (: /availability?date=all :)
  (: /availability?date=01-01-2021?date=02-02-2021... :)
};


(: ================ Cancel Reservation ================ :)
declare %updating
  %rest:path("/cancelreservation")
  %rest:query-param("id", "{$id}")
function page:cancel-reservation($id as xs:string)
{
  let $database := db:open("RGBDB")
 
  return if ($database//reservation[id = $id]/state = "Canceled")
  then ( 
        web:error(500, "[ERRO] A reserva já se encontra cancelada [ERRO]"))
  else (
  replace value of node $database//reservation[id = $id]/state with "Canceled",
  
  let $database := db:open("RGBDB")
  let $updateSlot := $database//reservation[id = $id]/date
  return replace value of node $database//a:reservations[a:date = $updateSlot]/a:slots with $database//a:reservations[a:date = $updateSlot]/a:slots + 1,
  update:output(page:canceledok($id))
   )
};


(: ================ Export DataBase ================ :)
declare
  %rest:path("/exportdatabase")
  %rest:GET
function page:exportdatabase() {
  db:export("RGBDB", "..\webapp\DB", map { 'method': 'xml' }),
  page:exportdone()
};

(: ================ Messages ================ :)
declare function page:canceledok($id) {
  (: return a message :)
  '[CANCELED] Reservation with code ' || $id ||' [CANCELED]'
};

declare function page:ok($date, $id) {
  (: return a message :)
  '[VALID] Reservation for the day ' || $date || ' accepted with code ' || $id || ' [VALID]'
};

declare function page:betweendates() {
  (: return a message :)
  '[ERROR] Choose dates between 16-09-2022 and 25-12-2022 [ERROR]'
};

declare function page:exportdone() {
  (: return a message :)
  '[EXPORTED] Database Exported with Success [EXPORTED]'
};