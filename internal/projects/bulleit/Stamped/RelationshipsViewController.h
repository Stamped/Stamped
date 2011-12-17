//
//  RelationshipsViewController.h
//  Stamped
//
//  Created by Andrew Bonventre on 8/31/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import <RestKit/RestKit.h>
#import <UIKit/UIKit.h>

#import "STViewController.h"

@class User;

typedef enum {
  RelationshipTypeFriends,
  RelationshipTypeFollowers
} RelationshipType;

@interface RelationshipsViewController : STViewController <RKObjectLoaderDelegate,
                                                           RKRequestDelegate,
                                                           UITableViewDelegate,
                                                           UITableViewDataSource> {
 @private
  RelationshipType relationshipType_;
}

@property (nonatomic, retain) IBOutlet UITableView* tableView;
@property (nonatomic, retain) User* user;

- (id)initWithRelationship:(RelationshipType)relationship;

@end
