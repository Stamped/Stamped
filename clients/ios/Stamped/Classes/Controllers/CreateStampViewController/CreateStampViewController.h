//
//  CreateStampViewController.h
//  Stamped
//
//  Created by Devin Doty on 6/12/12.
//
//

#import <UIKit/UIKit.h>

@interface CreateStampViewController : UITableViewController

- (id)initWithEntity:(id<STEntity>)entity;
- (id)initWithSearchResult:(id<STEntitySearchResult>)searchResult;


@end
