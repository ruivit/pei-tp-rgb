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
      <h2>This is a RESTful API for the [RuiGilbertoBruno API]</h2>
      <span style="padding-left:50px">
        <p></p>
      </span>
      <strong>Make a Reservation</strong>
      <br></br>
      <dd>
        <ul>
          <li>
            <code>POST /makereservation</code>
          </li>
        </ul>
      </dd>
      <span style="padding-left:15px">
        <p></p>
      </span>
      <strong>Check Availability</strong>
      <dd>
        <ul>
          <li>
            <code>GET /checkavailability?date="date"</code>
            <br></br>
            <cite>Availability for a certain day</cite>
            <span style="padding-left:25px">
              <p></p>
            </span>
          </li>
          <li>
            <code>GET /checkavailability?date="date"&amp;?date="date"...</code>
            <br></br>
            <cite>Availability for multiple days</cite>
            <span style="padding-left:25px">
              <p></p>
            </span>
          </li>
          <li>
            <code>GET /checkavailability?date="all"</code>
            <br></br>
            <cite>Availability for everyday in Atelier</cite>
            <span style="padding-left:25px">
              <p></p>
            </span>
          </li>
        </ul>
      </dd>
      <br></br>
      <span style="padding-left:15px">
        <p></p>
      </span>
      <strong>Cancel a Reservation</strong>
      <br></br>
      <dd>
        <ul>
          <li>
            <code>POST /cancelreservation?id="reservationID"</code>
          </li>
        </ul>
      </dd>
      <br></br>
      <span style="padding-left:15px">
        <p></p>
      </span>
      <strong>Export BaseX Database</strong>
      <br></br>
      <dd>
        <ul>
          <li>
            <code>GET /exportdatabase</code>
          </li>
        </ul>
      </dd>
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

  (:=== Se passar em todas as validações, então escreve na DB ===:)
  page:checks($xml)
};

(: ============= Checks ============= :)

declare %updating function page:checks($xml)
{
  let $database := db:open("RGBDB")
  let $pfDates := $xml//f:preferedDates
  let $atelierDates := $database//a:reservations
  
  (: Verifica se as datas preferidas da familia existem no Atelier,
  se não existirem, fica com o valor NULL :)
  let $existingDates := $atelierDates[a:date = $pfDates]
  (: Filtra as datas preferidas da família coincidentes com as do Atelier que têm slots disponíveis:)
  let $validSlots := $existingDates[a:slots > 0]
  (:Seleciona a primeira data com slots disponíveis, caso a 
  $existingDates esteja NULL a $validDate também fica NULL :)
  let $validDate := $validSlots[1]/a:date
  
  (: Verifica se as datas da família ainda não existem no Atelier.Esta filtragem foi implementada para se poder fazer criação automática de uma data, caso esta ainda não exista no Atelier :)
  let $notExistingDates := $pfDates[not(.=($atelierDates//a:date))]
  (:Verifica se a(s) data(s) da $notExistingDates se encontram 
  dentro do intervalo temporal dos 100 dias antes do Natal :)
  let $checkBetweenDates := page:check-between-dates($notExistingDates)
  (:Caso existam data(s) válida(s) seliciona a primeira:)
  let $newDate := $checkBetweenDates[1]
    
 (: Incrementa o elemento reservationID para +1 pois se tudo for validado, será criada uma nova reserva :)
  let $rid := $database//reservation[(last)]/id + 1
    
  return
  (:A variável $validDate pode estar com o valor NULL se não existirem dias preferidos coincidentes com os existentes no Atelier OU se os dias forem coincidentes, mas não houver slots disponíveis:)
  if ( empty($validDate) )
    (: Se a variável $newdate não for NULL, é porque traz uma data validada:)
  then ( if (empty($newDate))
         then ( web:error(500, "[ERRO] O atelier do Pai Natal atingiu o máximo de capacidade para o(s) dia(s) escolhidos ou as datas escolhidas não estão entre 2022-09-17 e 2022-12-25. [ERRO]") )
         else ( 
  (: A variável $newdate tráz uma data que será passada às funções new-date(arg1) e função return-xml-reservation(arg1,arg2):)
db:replace("RGBDB", "atelier.xml", page:new-date($newDate)),
db:add("RGBDB", page:return-xml-reservation($xml, $newDate), concat("reservation", count(db:open("RGBDB")//reservation) + 1, ".xml")),

(:========Mensagem de sucesso========:)
update:output(page:ok($newDate, $rid))
              )
       )
         
   else ( 
(: A variável $validDate traz uma data que vai ser passada à função return-xml-reservation(arg1,arg2) e no Atelier será decrementado um valor ao campo slots :)
replace value of node $database//a:reservations[a:date = $validDate]/a:slots with $database//a:reservations[a:date = $validDate]/a:slots - 1,
db:add("RGBDB", page:return-xml-reservation($xml, $validDate), concat("reservation", count(db:open("RGBDB")//reservation) + 1, ".xml")),

(:========Mensagem de sucesso========:)
update:output(page:ok($validDate, $rid))
      )
};


(:Verifica se a(s) data(s) da $notExistingDates se encontram 
  dentro do intervalo temporal dos 100 dias antes do Natal e retorna as datas válidas  :)
declare function page:check-between-dates($dateToCheck)
{
   
  for $validDays in $dateToCheck
  
  let $firstdate := xs:date("2022-09-17")
  let $lastdate := xs:date("2022-12-26")
  
  where some $days in $validDays satisfies $days>$firstdate and $days<$lastdate 

  return $validDays
};

(: Retorna um xml com uma nova data a ser adicionada ao Atelier já com as slots a 49,
 uma vez que vai ser criada uma reserva para este dia:)
declare function page:new-date($newDate)
{
  let $db := db:open("RGBDB")//a:atelier
  
  return 
  <atelier xmlns="http://www.atelierRGB.pt/Atelier" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.atelierRGB.pt/Atelier../XSD/Atelier.xsd">
  {$db//a:reservations}
 <reservations xmlns="http://www.atelierRGB.pt/Atelier" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
        <date>{$newDate/text()}</date>
        <slots>49</slots>
  </reservations>
</atelier>
};

(: Retorna um XML com a estrutura de uma reserva para a data que está na variável $reservationDate,
procura a última reserva lê o campo id e incrementa um valor para atribuir como id à nova reserva   :)
declare function page:return-xml-reservation($xml, $reservationDate)
{
  let $db := db:open("RGBDB")
  let $rid := $db//reservation[(last)]/id + 1
    
  return
  <reservation>
    <id>{$rid}</id>
    <date>{$reservationDate/text()}</date>
    <state>Active</state>
    <family>
      <numberElements>{count($xml//f:familyElement)}</numberElements>
      {$xml//f:familyElement}
      {$xml//f:origin}
    {$xml//f:emergencyContact}
    </family>
  </reservation>
};



(: ================ Verificar disponibilidade ================ :)

declare
  %rest:path("/availability")
  %rest:GET
  %rest:query-param("date", "{$getParam}")
    
(:Recebe os parâmetros enviados no GET request e em função dos mesmos executa diferentes operações:)  
function page:check-availability($getParam)
{
  (:Caso o parâmetro seja "all" verifica todos os dias existentes no Atelier e retorna o número de slots disponiveis :)
  if ($getParam = "all")
  then (
  let $database := db:open("RGBDB")
  let $atelierdates := $database//a:reservations
  
  
  for $x in $atelierdates
  order by data($x/a:date)
  return if ($x/a:slots = 0)
  then ("Não existe disponibilidade para o dia " || data($x/a:date))
  else (
  "Existe disponibilidade para " || $x/a:slots || " familias para o dia " || data($x/a:date)),
  (:Retorna mensagens segundo determinadas condições:)
  page:print-all-days()
  )

  else 
      (
    let $atelierDates := db:open("RGBDB")//a:atelier
    for $days in $getParam
    
    let $checkBetweenDates := page:check-between-dates($days)
    let $notExistingDates := $days[not(.=($checkBetweenDates))]
    
    let $slots := $atelierDates//a:reservations[a:date = $days]/a:slots/text()
    
    return if(empty($notExistingDates))
    then (
      if(empty($slots))
      then ("A data " || $days || " tem disponibilidade para 50 famílias.")
      else ("A data " || $days || " tem disponibilidade para " || $slots || " famílias."))
    else (
    "A data " || $notExistingDates || " nao se encontra dentro dos 100 dias")
      )
  
  (: GET REQUESTs Examples :)
  (: /availability?date=all :)
  (: /availability?date=01-01-2021?date=02-02-2021... :)
};

(: Como se tomou a decisão, de criar as datas no Atelier de forma automática, quando se faz uma verificação de disponibilidade para os 100 dias, teve de se considerar a possibilidade de ainda não haver reservas para todos o dias. Criou-se esta função para garantir que a informação prestada incluí as datas já existentes e todas as outras no intervalo de 2022-09-15 a 2022-09-23 :)
declare function page:print-all-days()
{
  let $database := db:open("RGBDB")
  let $count := count($database//a:date)
  
  return if ($count < 100)
  then ("Todos os restantes dias entre 2022-09-15 e 2022-12-23 têm disponibilidade para 50 famílias.")
  else ()
};


(: ================ Cancelar reservas ================ :)



declare %updating
  %rest:path("/cancelreservation")
  %rest:query-param("id", "{$id}")
function page:cancel-reservation($id as xs:string)
{
  try {
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
 } catch * {
   web:error(500, "[ERRO] O ID indicado não têm nenhuma reserva associada [ERRO]")
 }
   
};


(: ================ Export DataBase ================ :)
declare
  %rest:path("/exportdatabase")
  %rest:GET
function page:exportdatabase() {
  db:export("RGBDB", "..\webapp\DB", map { 'method': 'xml' }),
  page:exportdone()
};

(: ================ Auxiliary Function for generateData.py ================ 
It deletes the now old database and creates a new one that will get the random XMLs :)
declare %updating
  %rest:path("/DCDB")
  %rest:GET
function page:deleteAndCreateDB() {
  db:delete("RGBDB", "/"),
  db:create("RGBDB", "..\webapp\INITALDB")
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

declare function page:exportdone() {
  (: return a message :)
  '[EXPORTED] Database Exported with Success [EXPORTED]'
};
