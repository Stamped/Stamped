//
//  STUserStatsView.h
//  Stamped
//
//  Created by Devin Doty on 6/5/12.
//
//

#import <UIKit/UIKit.h>
#import "STUserHeaderView.h"

@protocol STUserStatsViewDelegate;
@class STStatButton, STSimpleUserDetail;
@interface STUserStatsView : UIView {
    STStatButton *_creditButton;
    STStatButton *_followersButton;
    STStatButton *_followingButton;
}

@property(nonatomic,assign) id <STUserStatsViewDelegate> delegate;

- (void)setupWithUser:(STSimpleUserDetail*)user;


@end
@protocol STUserStatsViewDelegate
- (void)stUserStatsView:(STUserStatsView*)view didSelectStat:(STUserHeaderStat)stat;
@end
