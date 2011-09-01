//
//  RelationshipsViewController.h
//  Stamped
//
//  Created by Andrew Bonventre on 8/31/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import <RestKit/RestKit.h>
#import <UIKit/UIKit.h>

#import "STReloadableTableViewController.h"

@class User;

typedef enum {
  RelationshipTypeFriends,
  RelationshipTypeFollowers
} RelationshipType;

@interface RelationshipsViewController : STReloadableTableViewController <RKObjectLoaderDelegate> {
 @private
  RelationshipType relationshipType_;
}

@property (nonatomic, retain) User* user;

- (id)initWithRelationship:(RelationshipType)relationship;

@end
