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

typedef enum {
    STUserHeaderStatCredit = 4,
    STUserHeaderStatFollowers,
    STUserHeaderStatFollowing,
} STUserHeaderStat;

@protocol STUserHeaderViewDelegate, STSimpleUserDetail;
@class UserStampView, STAvatarView, UserHeaderTabView, STUserStatsView;
@interface STUserHeaderView : UIView {
    UserHeaderTabView *_tabView;
    UserStampView *_stampView;
    UILabel *_titleLabel;
    UILabel *_detailTitleLabel;
    STUserStatsView *_statsView;
}

+ (CGFloat)heightWithStats:(BOOL)stats;

- (void)setupWithUser:(id)user;
@property(nonatomic,assign) STUserHeaderTab selectedTab;
@property(nonatomic, readwrite, assign) id <STUserHeaderViewDelegate> delegate;
@property(nonatomic,readonly,getter = isShowingStats) BOOL showingStats;

@end
@protocol STUserHeaderViewDelegate
- (void)stUserHeaderView:(STUserHeaderView*)view selectedTab:(STUserHeaderTab)tab;
- (void)stUserHeaderView:(STUserHeaderView*)view selectedStat:(STUserHeaderStat)stat;
- (void)stUserHeaderViewHeightChanged:(STUserHeaderView*)view;
- (void)stUserHeaderViewAvatarTapped:(STUserHeaderView*)view;
@end
