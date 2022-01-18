[{$unwind: {
    path: '$reservations'
   }}, {$group: {
    _id: '$reservations.family'
   }}, {$replaceRoot: {
    newRoot: '$_id'
   }}, {$project: {
    _id: 0,
    familyElement: 1,
    numberElements: 1
   }}, {$out: 'families'}]