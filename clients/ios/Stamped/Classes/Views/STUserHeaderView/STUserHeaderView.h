//
//  STUserHeaderView.h
//  Stamped
//
//  Created by Devin Doty on 6/5/12.
//
//

#import <UIKit/UIKit.h>

typedef enum {
    STUserHeaderTabStamps = 1,
    STUserHeaderTabGraph,
    STUserHeaderTabInfo,
} STUserHeaderTab;

@protocol STUserHeaderViewDelegate;
@class UserStampView, STAvatarView, UserHeaderTabView;
@interface STUserHeaderView : UIView {
    UserHeaderTabView *_tabView;
    STAvatarView *_avatarView;
    UserStampView *_stampView;
    UILabel *_titleLabel;
    UILabel *_detailTitleLabel;
}

- (void)setupWithUser:(id<STUser>)user;
@property(nonatomic,assign) STUserHeaderTab selectedTab;
@property(nonatomic,assign) id <STUserHeaderViewDelegate> delegate;
@property(nonatomic,assign) BOOL showStats;

@end
@protocol STUserHeaderViewDelegate
- (void)stUserHeaderView:(STUserHeaderView*)view selectedTab:(STUserHeaderTab)tab;
- (void)stUserHeaderViewHeightChanged:(STUserHeaderView *)view;
@end
