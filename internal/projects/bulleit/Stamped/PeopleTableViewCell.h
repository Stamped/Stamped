//
//  PeopleTableViewCell.h
//  Stamped
//
//  Created by Andrew Bonventre on 8/17/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>

@class PeopleCellView;
@class User;

@interface PeopleTableViewCell : UITableViewCell {
 @protected
  PeopleCellView* customView_;
}

- (id)initWithReuseIdentifier:(NSString*)reuseIdentifier;

@property (nonatomic, retain) User* user;
@property (nonatomic, assign) BOOL disclosureArrowHidden;

@end
