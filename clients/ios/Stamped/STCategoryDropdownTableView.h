//
//  STCategoryDropdownTableView.h
//  Stamped
//
//  Created by Andrew Bonventre on 8/29/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>

typedef enum {
  STEditCategoryRowFood = 0,
  STEditCategoryRowBooks,
  STEditCategoryRowFilm,
  STEditCategoryRowMusic,
  STEditCategoryRowOther
} STEditCategoryRow;

@interface STCategoryDropdownTableView : UITableView <UITableViewDataSource>

@end
