//
//  ActivityCreditTableViewCell.h
//  Stamped
//
//  Created by Andrew Bonventre on 8/1/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>

@class Event;

@interface ActivityCreditTableViewCell : UITableViewCell

- (id)initWithReuseIdentifier:(NSString*)reuseIdentifier;

@property (nonatomic, retain) Event* event;

@end
