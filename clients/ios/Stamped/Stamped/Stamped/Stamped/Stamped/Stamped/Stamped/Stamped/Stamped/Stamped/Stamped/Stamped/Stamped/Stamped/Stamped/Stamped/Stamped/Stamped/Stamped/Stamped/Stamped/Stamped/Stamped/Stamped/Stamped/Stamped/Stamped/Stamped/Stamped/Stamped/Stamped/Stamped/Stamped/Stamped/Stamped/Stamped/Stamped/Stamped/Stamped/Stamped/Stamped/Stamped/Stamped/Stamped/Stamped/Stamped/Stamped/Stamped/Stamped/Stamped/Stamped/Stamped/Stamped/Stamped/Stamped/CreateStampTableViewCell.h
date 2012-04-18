//
//  CreateStampTableViewCell.h
//  Stamped
//
//  Created by Andrew Bonventre on 7/23/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>

@class Entity;
@class CreateStampCellView;

@interface CreateStampTableViewCell : UITableViewCell {
@private  
  CreateStampCellView* customView_;
}

- (id)initWithReuseIdentifier:(NSString*)reuseIdentifier;

@property (nonatomic, retain) Entity* entityObject;

@end
