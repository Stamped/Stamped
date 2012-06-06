//
//  STUserGraphView.h
//  Stamped
//
//  Created by Devin Doty on 6/5/12.
//
//

#import <UIKit/UIKit.h>

@protocol STUserGraphViewDelegate;
@interface STUserGraphView : UIView {
    UILabel *_countLabel;
    UIView *_graphContainer;
    UIView *_calloutView;
}

@property(nonatomic,assign) id <STUserGraphViewDelegate> delegate;

- (void)setupWithUser:(id)user;

@end
@protocol STUserGraphViewDelegate
- (void)stUserGraphView:(STUserGraphView*)view selectedCategory:(NSString*)category;
@end
