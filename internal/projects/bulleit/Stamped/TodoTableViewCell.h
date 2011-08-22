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

@interface TodoTableViewCell : UITableViewCell {
 @private
  CTFontRef titleFont_;
  CTParagraphStyleRef titleStyle_;
  NSMutableDictionary* titleAttributes_;
}

- (id)initWithReuseIdentifier:(NSString*)reuseIdentifier;

@property (nonatomic, assign) BOOL completed;
@property (nonatomic, retain) Entity* entityObject;

@end
