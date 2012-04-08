//
//  PeopleListViewController.h
//  Stamped
//
//  Created by Andrew Bonventre on 8/31/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import <RestKit/RestKit.h>
#import <UIKit/UIKit.h>

#import "STViewController.h"

@class Stamp;
@class User;

typedef enum {
  PeopleListSourceTypeFriends,
  PeopleListSourceTypeFollowers,
  PeopleListSourceTypeLikes,
  PeopleListSourceTypeCredits
} PeopleListSourceType;

@interface PeopleListViewController : STViewController <RKObjectLoaderDelegate,
                                                        RKRequestDelegate,
                                                        UITableViewDelegate,
                                                        UITableViewDataSource> {
 @private
  PeopleListSourceType sourceType_;
}

@property (nonatomic, retain) IBOutlet UITableView* tableView;
@property (nonatomic, retain) User* user;
@property (nonatomic, retain) Stamp* stamp;

- (id)initWithSource:(PeopleListSourceType)sourceType;

@end
