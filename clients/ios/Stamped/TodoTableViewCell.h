//
//  TodoTableViewCell.h
//  Stamped
//
//  Created by Andrew Bonventre on 8/21/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import <CoreText/CoreText.h>
#import <UIKit/UIKit.h>

@class Entity;
@class Favorite;
@class Stamp;
@class TodoTableViewCell;

@protocol TodoTableViewCellDelegate
- (void)todoTableViewCell:(TodoTableViewCell*)cell shouldStampEntity:(Entity*)entity;
- (void)todoTableViewCell:(TodoTableViewCell*)cell shouldShowStamp:(Stamp*)stamp;
@end

@interface TodoTableViewCell : UITableViewCell {
 @private
  CTFontRef titleFont_;
  CTParagraphStyleRef titleStyle_;
  NSMutableDictionary* titleAttributes_;
}

- (id)initWithReuseIdentifier:(NSString*)reuseIdentifier;

@property (nonatomic, retain) Favorite* favorite;
@property (nonatomic, assign) id<TodoTableViewCellDelegate> delegate;

@end
