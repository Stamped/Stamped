//
//  STActionView.h
//  Stamped
//
//  Created by Devin Doty on 5/16/12.
//
//

#import <UIKit/UIKit.h>
#import "STDetailActionItem.h"
#import "STStamp.h"

@protocol STActionViewDelegate;
@interface STDetailActionView : UIView {
    NSArray *_itemViews;
}

- (id)initWithStamp:(id<STStamp>)stamp delegate:(id)delegate;
- (id)initWithItems:(NSArray<STDetailActionItem>*)items;

@property(nonatomic,assign) NSInteger minItemsToShow; // default 4
@property(nonatomic,assign) BOOL expanded;
@property(nonatomic,assign) id <STActionViewDelegate> delegate;
@property(nonatomic,retain) NSArray <STDetailActionItem> *items;

- (void)setExpanded:(BOOL)expanded animated:(BOOL)animated;

@end
@protocol STActionViewDelegate
- (void)stActionView:(STDetailActionView*)view itemSelectedAtIndex:(NSInteger)index;
@end