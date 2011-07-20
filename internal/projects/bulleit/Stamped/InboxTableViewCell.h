//
//  InboxTableViewCell.h
//  Stamped
//
//  Created by Andrew Bonventre on 7/12/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>

@class StampCellView;
@class Stamp;

@interface InboxTableViewCell : UITableViewCell {
 @private  
  StampCellView* customView_;
}

- (id)initWithReuseIdentifier:(NSString*)reuseIdentifier;

@property (nonatomic, retain) Stamp* stamp;

@end
