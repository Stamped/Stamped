//
//  PostStampGraphView.h
//  Stamped
//
//  Created by Devin Doty on 6/14/12.
//
//

#import <UIKit/UIKit.h>

@interface PostStampGraphView : UIView {
    UIImageView *_imageView;
    CATextLayer *_titleLayer;
    UIView *_graphContainer;
    UIActivityIndicatorView *_activityView;
}

@property(nonatomic,retain) id<STUserDetail> user;
@property(nonatomic,retain) NSString *category;
@property(nonatomic,assign) BOOL loading;
@end
