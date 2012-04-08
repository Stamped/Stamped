//
//  CreditTableViewCell.h
//  Stamped
//
//  Created by Andrew Bonventre on 10/1/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>

@class Stamp;
@class User;

@interface CreditTableViewCell : UITableViewCell

- (id)initWithReuseIdentifier:(NSString*)reuseIdentifier;

@property (nonatomic, retain) Stamp* stamp;
@property (nonatomic, retain) User* creditedUser;

@end
