db.families.aggregate(
[{$group: {
    _id: null,
    TotalNumberElements: {
     $sum: '$numberElements'
    },
    AVGNE: {
     $avg: '$numberElements'
    }
   }}, {$project: {
    _id: 0,
    TotalNumberElements: 1,
    AverageNumberElementsPerFamily: {
     $round: [
      '$AVGNE',
      1
     ]
    }
   }}]
).pretty()